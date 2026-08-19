import json
from datetime import datetime, timezone

from flask import request, jsonify

from app.models.grade import Grade
from app.models.ai_edit import AIEdit
from app.models.lesson import Lesson
from app.models.lesson_submission import LessonSubmission
from app.models.user_profile import UserProfile
from app.utils.auth import get_user_from_token
from app.utils.ai_grading import is_class_teacher, dump_grade, notify
from app.controllers.lessons.grade_essay import _student_name


def _get_lesson(lesson_id):
    return Lesson.get_or_none(Lesson.id == lesson_id)


def _teacher_guard(user, lesson):
    return is_class_teacher(user, lesson.class_ref)


def _grade_for_lesson(grade, lesson_id):
    if grade.lesson_submission_id:
        return grade.lesson_submission.lesson_id == lesson_id
    return False


def _essays_for_submission(submission, lesson):
    try:
        results = (
            json.loads(submission.results_json)
            if isinstance(submission.results_json, str)
            else (submission.results_json or {})
        )
    except (ValueError, TypeError):
        results = {}

    try:
        content = (
            json.loads(lesson.content_json)
            if isinstance(lesson.content_json, str)
            else (lesson.content_json or [])
        )
    except (ValueError, TypeError):
        content = []

    essays = []
    for i, block in enumerate(content):
        if not isinstance(block, dict) or block.get("type") != "essay":
            continue
        entry = results.get(str(i)) or results.get(i) or {}
        answer = entry.get("value") if isinstance(entry, dict) else None
        answer_text = answer or ""
        if not str(answer_text).strip():
            continue
        essays.append(
            {
                "block_index": i,
                "question": block.get("title") or "",
                "placeholder": block.get("placeholder") or "",
                "max_length": block.get("max_length"),
                "answer": answer_text,
            }
        )
    return essays


def list_grades_handler(lesson_id):
    user, _, error = get_user_from_token()
    if error:
        return error

    lesson = _get_lesson(lesson_id)
    if not lesson:
        return jsonify({"error": "lesson not found"}), 404
    if not _teacher_guard(user, lesson):
        return jsonify({"error": "forbidden"}), 403

    submissions = (
        LessonSubmission.select()
        .where(LessonSubmission.lesson == lesson_id)
        .order_by(LessonSubmission.submitted_at.desc())
    )

    data = []
    for s in submissions:
        grades = list(
            Grade.select()
            .where(Grade.lesson_submission == s.id)
            .order_by(Grade.block_index.asc())
        )
        data.append(
            {
                "id": s.id,
                "user_id": s.user_id,
                "user_name": _student_name(s),
                "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
                "essays": _essays_for_submission(s, lesson),
                "grades": [dump_grade(g) for g in grades],
            }
        )

    return jsonify({"data": data})


def approve_grade_handler(lesson_id, grade_id):
    user, _, error = get_user_from_token()
    if error:
        return error

    lesson = _get_lesson(lesson_id)
    if not lesson:
        return jsonify({"error": "lesson not found"}), 404
    if not _teacher_guard(user, lesson):
        return jsonify({"error": "forbidden"}), 403

    grade = Grade.get_or_none(Grade.id == grade_id)
    if not grade or not _grade_for_lesson(grade, lesson_id):
        return jsonify({"error": "grade not found"}), 404

    grade.status = "approved"
    grade.save()

    submission = grade.lesson_submission
    notify(
        submission.user_id,
        "grade_released",
        {
            "lesson_id": lesson.id,
            "lesson_title": lesson.title,
            "grade_id": grade.id,
            "score": grade.score,
        },
    )

    return jsonify({"data": dump_grade(grade)})


def override_grade_handler(lesson_id, grade_id):
    user, _, error = get_user_from_token()
    if error:
        return error

    lesson = _get_lesson(lesson_id)
    if not lesson:
        return jsonify({"error": "lesson not found"}), 404
    if not _teacher_guard(user, lesson):
        return jsonify({"error": "forbidden"}), 403

    grade = Grade.get_or_none(Grade.id == grade_id)
    if not grade or not _grade_for_lesson(grade, lesson_id):
        return jsonify({"error": "grade not found"}), 404

    payload = request.get_json(silent=True) or {}

    AIEdit.create(
        target_table="grades",
        target_id=grade.id,
        original_content=json.dumps(
            {"score": grade.score, "feedback": grade.feedback}, ensure_ascii=False
        ),
        edited_content=json.dumps(
            {"score": payload.get("score"), "feedback": payload.get("feedback")},
            ensure_ascii=False,
        ),
        editor_service="guru",
        user=user,
        created_at=datetime.now(timezone.utc),
    )

    if "score" in payload:
        try:
            grade.score = int(payload.get("score"))
        except (TypeError, ValueError):
            return jsonify({"error": "score must be integer"}), 400
    if "feedback" in payload:
        grade.feedback = payload.get("feedback")

    grade.status = "modified"
    grade.save()

    submission = grade.lesson_submission
    notify(
        submission.user_id,
        "grade_released",
        {
            "lesson_id": lesson.id,
            "lesson_title": lesson.title,
            "grade_id": grade.id,
            "score": grade.score,
        },
    )

    return jsonify({"data": dump_grade(grade)})