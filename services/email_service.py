"""
Reusable email sending logic, kept separate from the Django view so
it can be tested or reused on its own without needing an HTTP request
to trigger it.
"""

import logging
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger("api")


def send_application_email(to_email: str, subject: str, body: str, resume_path: Path) -> tuple[bool, str]:
    """
    Sends a plain text email with the given resume attached as a PDF.

    Returns a (success, message) tuple instead of raising, so the
    calling view can decide what HTTP status and response body to
    return without having to wrap this call in its own try/except.
    """
    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )

        with open(resume_path, "rb") as resume_file:
            email.attach(resume_path.name, resume_file.read(), "application/pdf")

        # fail_silently=False means SMTP errors raise an exception here
        # instead of getting swallowed, which is what we want since we
        # need to know whether the send actually worked.
        email.send(fail_silently=False)

        logger.info(f"Email sent successfully to {to_email}")
        return True, "Application sent"

    except Exception as exc:
        logger.error(f"Failed to send email to {to_email}: {exc}")
        return False, f"Failed to send email: {exc}"
