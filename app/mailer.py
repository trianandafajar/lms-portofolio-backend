import smtplib
from email.mime.text import MIMEText
from app.config import MAIL_HOST, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER


def send_email(subject: str, body: str, to_email: str, to_name: str = None):
    """
    Generic SMTP email sender.
    """
    recipient = f"{to_name} <{to_email}>" if to_name else to_email

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = MAIL_DEFAULT_SENDER
    msg["To"] = recipient

    with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()


def send_subscription_email(to_email: str, plan_name: str):
    """
    Send a subscription success email using Mailtrap.
    """
    subject = f"Subscription to {plan_name} Successful 🎉"
    body = f"""
Hello 👋,

Thank you for subscribing to the {plan_name} plan.
Your subscription is now active and ready to use.

Best regards,
The Support Team
"""

    send_email(subject, body, to_email)