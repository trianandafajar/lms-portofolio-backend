from flask import request, jsonify
from peewee import IntegrityError

from app.models.lesson import Lesson
from app.models.lms_class import LmsClass
from app.models.user import User
from app.schemas.lesson import LessonSchema

schema = LessonSchema()


def create_lesson_handler():
    payload = request.get_json(silent=True) or {}

    class_id = payload.get("class_id")
    title = payload.get("title")
    author_id = payload.get("author_id")
    summary = payload.get("summary")
    content = payload.get("content")
    content_json = payload.get("content_json")
    is_published = payload.get("is_published", False)

    if not class_id or not title or not author_id:
        return jsonify({"error": "class_id, title, author_id are required"}), 400

    if not LmsClass.get_or_none(LmsClass.id == class_id):
        return jsonify({"error": "class not found"}), 404
    if not User.get_or_none(User.id == author_id):
        return jsonify({"error": "author not found"}), 404

    try:
        row = Lesson.create(
            class_ref=class_id,
            title=title,
            author=author_id,
            summary=summary,
            content=content,
            content_json=content_json,
            is_published=bool(is_published),
        )
    except IntegrityError:
        return jsonify({"error": "failed to create lesson"}), 400

    return jsonify(schema.dump(row)), 201
