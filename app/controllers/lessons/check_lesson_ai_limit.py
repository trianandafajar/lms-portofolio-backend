from flask import jsonify
from app.utils.auth import get_user_from_token
from app.models.lesson import Lesson
from app.utils.subscription_limits import check_ai_limit


def check_lesson_ai_limit_handler(lesson_id):
    user, _, error = get_user_from_token()
    if error:
        return error

    lesson = Lesson.get_or_none(Lesson.id == lesson_id)
    if not lesson:
        return jsonify({"error": "lesson not found"}), 404

    creator_id = lesson.class_ref.creator_id
    allowed, err_resp, status_code = check_ai_limit(creator_id)
    if not allowed:
        return err_resp, status_code

    return jsonify({"success": True, "message": "AI usage within limits"}), 200