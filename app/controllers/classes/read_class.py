from flask import request, jsonify
from app.models.lms_class import LmsClass
from app.schemas.lms_class import ClassListSchema, ClassDetailSchema

list_schema = ClassListSchema(many=True)
detail_schema = ClassDetailSchema()


def read_class_handler(class_id=None):
    if class_id is not None:
        row = LmsClass.get_or_none(LmsClass.id == class_id)
        if not row:
            return jsonify({"error": "class not found"}), 404
        return jsonify(detail_schema.dump(row))

    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except ValueError:
        page = 1
        per_page = 20
    if per_page > 100:
        per_page = 100

    query = LmsClass.select().order_by(LmsClass.id)
    rows = list(query.paginate(page, per_page))
    return jsonify({
        "data": list_schema.dump(rows),
        "page": page,
        "per_page": per_page,
    })
