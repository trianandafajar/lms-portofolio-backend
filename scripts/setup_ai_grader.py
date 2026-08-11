from werkzeug.security import generate_password_hash
from app.db import database
from app.config import init_database_from_env
from app.models.user import User, Role, UserRole
from app.models.user_profile import UserProfile
from datetime import datetime

AI_GRADER_EMAIL = "ai-grader@mentora.local"


def seed_ai_grader():
    now = datetime.utcnow()

    user, created = User.get_or_create(
        email=AI_GRADER_EMAIL,
        defaults={
            "password_hash": generate_password_hash(__import__("secrets").token_hex(24)),
            "is_active": False,
            "created_at": now,
            "updated_at": now,
        },
    )

    if not created:
        user.is_active = False
        user.updated_at = now
        user.save()

    try:
        role = Role.get(Role.name == "admin")
        UserRole.get_or_create(user=user, role=role)
    except Role.DoesNotExist:
        print("⚠️ Role 'admin' does not exist — run the roles seeder first.")

    UserProfile.get_or_create(
        user=user,
        defaults={
            "display_name": "AI Grader",
            "bio": "System account used for AI-assisted essay grading.",
            "extra": "{}",
            "created_at": now,
            "updated_at": now,
        },
    )

    if created:
        print(f"✅ AI Grader user created: {AI_GRADER_EMAIL} (id={user.id})")
    else:
        print(f"ℹ️ AI Grader user already exists (id={user.id})")

    return user.id


if __name__ == "__main__":
    init_database_from_env()
    if database.is_closed():
        database.connect()

    seed_ai_grader()

    if not database.is_closed():
        database.close()