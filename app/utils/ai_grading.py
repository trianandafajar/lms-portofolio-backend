import json
from datetime import datetime, timezone

from app.models.user import User
from app.models.grade import Grade
from app.models.class_membership import ClassMembership
from app.models.notification import Notification

AI_GRADER_EMAIL = "ai-grader@mentora.local"


def get_ai_grader():
    return User.get_or_none(User.email == AI_GRADER_EMAIL)


def is_class_teacher(user, class_ref):
    if not user or not class_ref:
        return False
    if user.id == class_ref.creator_id:
        return True
    return (
        ClassMembership.select()
        .where(
            (ClassMembership.class_ref == class_ref.id)
            & (ClassMembership.user == user.id)
            & (ClassMembership.role.in_(["teacher", "admin"]))
        )
        .exists()
    )


def dump_grade(grade):
    grader = grade.grader
    grader_ai = bool(grader) and grader.email == AI_GRADER_EMAIL
    return {
        "id": grade.id,
        "lesson_submission_id": grade.lesson_submission_id,
        "block_index": grade.block_index,
        "score": grade.score,
        "feedback": grade.feedback,
        "status": grade.status or "draft",
        "graded_at": grade.graded_at.isoformat() if grade.graded_at else None,
        "grader": {
            "id": grader.id if grader else None,
            "name": getattr(grader, "email", "unknown"),
            "is_ai": grader_ai,
        },
    }


def notify(user_id, type, payload):
    if not user_id:
        return
    try:
        Notification.create(
            user=user_id,
            type=type,
            payload=json.dumps(payload or {}, ensure_ascii=False),
            is_read=False,
            created_at=datetime.now(timezone.utc),
        )
    except Exception:
        pass