from flask import request, jsonify
from peewee import IntegrityError
from datetime import datetime, timezone

from app.models.grade import Grade
from app.models.submission import Submission
from app.models.lesson_submission import LessonSubmission
from app.models.user import User
from app.schemas.grade import GradeSchema

schema = GradeSchema()


def create_grade_handler():
    payload = request.get_json(silent=True) or {}

    submission_id = payload.get("submission_id")
    lesson_submission_id = payload.get("lesson_submission_id")
    grader_id = payload.get("grader_id")
    score = payload.get("score")

    if score is None or grader_id is None:
        return jsonify({"error": "grader_id and score are required"}), 400

    if not submission_id and not lesson_submission_id:
        return jsonify({"error": "submission_id or lesson_submission_id are required"}), 400

    if not User.get_or_none(User.id == grader_id):
        return jsonify({"error": "grader not found"}), 404

    if submission_id and not Submission.get_or_none(Submission.id == submission_id):
        return jsonify({"error": "submission not found"}), 404

    if lesson_submission_id and not LessonSubmission.get_or_none(
        LessonSubmission.id == lesson_submission_id
    ):
        return jsonify({"error": "lesson submission not found"}), 404

    try:
        row = Grade.create(
            submission=submission_id or None,
            lesson_submission=lesson_submission_id or None,
            grader=grader_id,
            score=int(score),
            feedback=payload.get("feedback"),
            status=payload.get("status") or "draft",
            graded_at=datetime.now(timezone.utc),
        )
    except IntegrityError:
        return jsonify({"error": "failed to create grade"}), 400

    return jsonify(schema.dump(row)), 201