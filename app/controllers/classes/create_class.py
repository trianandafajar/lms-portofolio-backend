from flask import request, jsonify
from peewee import IntegrityError

from app.models.lms_class import LmsClass
from app.models.user import User
from app.schemas.lms_class import ClassListSchema
from app.utils.auth import get_user_from_token

schema = ClassListSchema()


def create_class_handler():
    user, error = get_user_from_token()
    if error:
        return error

    payload = request.get_json(silent=True) or {}

    title = payload.get("title")
    code = payload.get("code")
    creator_id = payload.get("creator_id") or user.id
    description = payload.get("description")
    visibility = payload.get("visibility", "private")

    if not title or not code:
        return jsonify({"error": "title and code are required"}), 400

    if not User.get_or_none(User.id == creator_id):
        return jsonify({"error": "creator not found"}), 404

    try:
        row = LmsClass.create(
            title=title,
            code=code,
            creator=creator_id,
            description=description,
            visibility=visibility,
        )
    except IntegrityError:
        return jsonify({"error": "code already exists"}), 409

    return jsonify(schema.dump(row)), 201
