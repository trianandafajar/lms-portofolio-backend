from flask import request, jsonify
from app.models.lms_class import LmsClass
from app.models.class_membership import ClassMembership
from app.schemas.lms_class import ClassListSchema
from app.utils.auth import get_user_from_token
from peewee import JOIN

list_schema = ClassListSchema(many=True)

def read_my_class_handler():
    user, error = get_user_from_token()
    if error:
        return error

    # pagination
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except ValueError:
        page = 1
        per_page = 20
    if per_page > 100:
        per_page = 100

    creator_query = LmsClass.select().where(LmsClass.creator == user)

    member_query = (
        LmsClass
        .select(LmsClass)
        .join(ClassMembership, on=(ClassMembership.class_ref == LmsClass.id))
        .where(
            (ClassMembership.user == user) &
            (ClassMembership.is_active == True)
        )
    )

    class_ids = set([c.id for c in creator_query] + [c.id for c in member_query])
    query = LmsClass.select().where(LmsClass.id.in_(class_ids)).order_by(LmsClass.id)
    rows = list(query.paginate(page, per_page))

    return jsonify({
        "data": list_schema.dump(rows),
        "page": page,
        "per_page": per_page,
    })