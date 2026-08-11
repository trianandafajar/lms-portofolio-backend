import json
from datetime import datetime, timezone

from flask import request, jsonify

from app.models.grade import Grade
from app.models.ai_edit import AIEdit
from app.models.lesson_submission import LessonSubmission
from app.models.lesson import Lesson
from app.models.user_profile import UserProfile
from app.utils.auth import get_user_from_token
from app.utils.ai_grading import get_ai_grader, is_class_teacher, dump_grade, notify


def _extract_essay_answer(submission, block_index):
    try:
        results = json.loads(submission.results_json) if isinstance(submission.results_json, str) else (submission.results_json or {})
    except (ValueError, TypeError):
        results = {}
    entry = results.get(block_index) if isinstance(block_index, int) else None
    if entry is None:
        entry = results.get(str(block_index))
    if isinstance(entry, dict):
        return entry.get("value") or ""
    return ""


def _student_name(submission):
    profile = UserProfile.get_or_none(UserProfile.user == submission.user_id)
    if profile and profile.display_name:
        return profile.display_name
    return getattr(submission.user, "email", "Student")


def grade_essay_handler(lesson_id):
    user, _, error = get_user_from_token()
    if error:
        return error

    payload = request.get_json(silent=True) or {}
    lesson_submission_id = payload.get("lesson_submission_id")
    block_index = payload.get("block_index")
    ai_result = payload.get("ai_result") or {}

    if not lesson_submission_id or block_index is None:
        return jsonify({"error": "lesson_submission_id and block_index are required"}), 400

    submission = LessonSubmission.get_or_none(LessonSubmission.id == lesson_submission_id)
    if not submission or submission.lesson_id != lesson_id:
        return jsonify({"error": "lesson submission not found"}), 404

    lesson = submission.lesson

    if user.id != submission.user_id and not is_class_teacher(user, lesson.class_ref):
        return jsonify({"error": "forbidden"}), 403

    existing = (
        Grade.select()
        .where(
            (Grade.lesson_submission == submission.id)
            & (Grade.block_index == block_index)
        )
        .order_by(Grade.id.desc())
        .first()
    )
    if existing:
        return jsonify({"data": dump_grade(existing)}), 200

    if not submission.results_json:
        return jsonify({"error": "submission has no answers to grade"}), 400

    grader = get_ai_grader()
    if not grader:
        return (
            jsonify(
                {
                    "error": "AI grader service user not found. Run: python scripts/setup_ai_grader.py"
                }
            ),
            500,
        )

    answer = _extract_essay_answer(submission, block_index)
    if not answer or not str(answer).strip():
        return jsonify({"data": None, "message": "empty essay answer, skipped"}), 200

    score = ai_result.get("score")
    if score is None:
        return jsonify({"error": "ai_result.score is required"}), 400

    feedback_parts = [str(ai_result.get("feedback") or "")]
    if ai_result.get("suggested_improvement"):
        feedback_parts.append("Saran: " + str(ai_result.get("suggested_improvement")))
    feedback = "\n".join(p for p in feedback_parts if p) or None

    grade = Grade.create(
        lesson_submission=submission,
        block_index=int(block_index),
        grader=grader,
        score=int(score),
        feedback=feedback,
        status="draft",
        graded_at=datetime.now(timezone.utc),
    )

    AIEdit.create(
        target_table="grades",
        target_id=grade.id,
        original_content=json.dumps(
            {"block_index": block_index, "answer": answer}, ensure_ascii=False
        ),
        edited_content=json.dumps(
            {"score": int(score), "feedback": feedback}, ensure_ascii=False
        ),
        editor_service="gemini",
        user=grader,
        created_at=datetime.now(timezone.utc),
    )

    notify(
        lesson.class_ref.creator_id,
        "grading_ready",
        {
            "lesson_id": lesson.id,
            "lesson_title": lesson.title,
            "student_name": _student_name(submission),
            "grade_id": grade.id,
            "score": int(score),
        },
    )

    return jsonify({"data": dump_grade(grade)}), 201