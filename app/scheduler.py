from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.models.assignment import Assignment
from app.models.class_membership import ClassMembership
from app.models.submission import Submission
from app.utils.ai_grading import notify
from app.mailer import send_email

scheduler = BackgroundScheduler()
_started = False


def _has_submitted(assignment_id, user_id):
    return (
        Submission.select()
        .where(
            (Submission.assignment == assignment_id)
            & (Submission.user == user_id)
        )
        .exists()
    )


def send_upcoming_deadline_reminders():
    """Send H-1 reminders to students who have not submitted an assignment due tomorrow."""
    now = datetime.utcnow()
    start = now + timedelta(days=1)
    end = start + timedelta(days=1)

    assignments = list(
        Assignment.select()
        .where((Assignment.due_at >= start) & (Assignment.due_at < end))
        .order_by(Assignment.due_at)
    )

    for assignment in assignments:
        members = list(
            ClassMembership.select().where(ClassMembership.class_ref == assignment.class_id)
        )
        class_title = assignment.class_ref.title if assignment.class_ref else "Class"
        for member in members:
            if member.role in ("teacher", "admin"):
                continue
            if _has_submitted(assignment.id, member.user_id):
                continue

            notify(
                member.user_id,
                "deadline_reminder",
                {
                    "assignment_id": assignment.id,
                    "assignment_title": assignment.title,
                    "class_title": class_title,
                    "due_at": assignment.due_at.isoformat() if assignment.due_at else None,
                },
            )

            body = (
                f"Hello,\n\n"
                f'Just a reminder, the assignment "{assignment.title}" '
                f'for class "{class_title}" is due tomorrow.\n\n'
                "Please make sure you submit before the deadline.\n\n"
                "Best regards,\nMentora"
            )
            try:
                send_email(
                    f"Mentora: Deadline reminder - {assignment.title}",
                    body,
                    member.user.email,
                )
            except Exception as exc:
                print(f"[scheduler] failed to send email to {member.user.email}: {exc}")

    return len(assignments)


def send_overdue_summaries():
    """Send a summary to teachers for assignments past due within the last 24 hours."""
    now = datetime.utcnow()
    start = now - timedelta(days=1)

    assignments = list(
        Assignment.select()
        .where((Assignment.due_at >= start) & (Assignment.due_at < now))
        .order_by(Assignment.due_at)
    )

    for assignment in assignments:
        members = list(
            ClassMembership.select().where(ClassMembership.class_ref == assignment.class_id)
        )
        not_submitted = [
            m for m in members if m.role not in ("teacher", "admin") and not _has_submitted(assignment.id, m.user_id)
        ]
        if not not_submitted:
            continue

        names = []
        for m in not_submitted:
            profile = getattr(m.user, "profile", None)
            names.append(profile.display_name if profile and profile.display_name else m.user.email)

        notify(
            assignment.creator_id,
            "deadline_overdue_summary",
            {
                "assignment_id": assignment.id,
                "assignment_title": assignment.title,
                "due_at": assignment.due_at.isoformat() if assignment.due_at else None,
                "not_submitted_count": len(names),
                "not_submitted_names": names[:20],
            },
        )

    return len(assignments)


def ensure_scheduler_started():
    global _started
    if _started:
        return
    scheduler.add_job(
        send_upcoming_deadline_reminders,
        CronTrigger(hour=6, minute=0),
        id="deadline_reminder_h1",
        replace_existing=True,
    )
    scheduler.add_job(
        send_overdue_summaries,
        CronTrigger(hour=6, minute=15),
        id="deadline_overdue_summary",
        replace_existing=True,
    )
    scheduler.start()
    _started = True
    print("✅ APScheduler started (deadline reminder jobs)")