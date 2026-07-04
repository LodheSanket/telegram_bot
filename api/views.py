import logging

from rest_framework import status
from rest_framework import response
from rest_framework.permissions import AllowAny
from rest_framework.response import Response 
from rest_framework.views import APIView

from bot.telegram_bot import DJANGO_API_URL
from services.email_service import send_application_email
from services.resume_mapper import get_resume_path
from services.templates import SUBJECT_TEMPLATES, TEMPLATES

from .authentication import APIKeyAuthentication
from .models import ApplicationHistory
from .serializers import ApplyRequestSerializer
from threading import Thread
logger = logging.getLogger("api")


def send_email_in_background(email, role, subject, body, resume_path):
    """
    Runs in a background thread so the API can return immediately.
    """

    success, message = send_application_email(
        email,
        subject,
        body,
        resume_path,
    )

    ApplicationHistory.objects.create(
        recipient_email=email,
        role=role,
        status="sent" if success else "failed",
    )

    if success:
        logger.info(f"Email sent to {email} for role {role}")
    else:
        logger.error(f"Email failed for {email}: {message}")


class ApplyView(APIView):
    """
    Handles POST /api/apply/. This is the only endpoint the Telegram
    bot calls. Given an email and a role, it picks the matching resume
    and email template, sends the email, records the attempt in
    ApplicationHistory, and reports back whether it worked.
    """
    
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info(f"Apply request received: {request.data}")
        

        serializer = ApplyRequestSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Validation failed: {serializer.errors}")
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        role = serializer.validated_data["role"]

        resume_path = get_resume_path(role)
        if resume_path is None:
            logger.error(f"Resume file missing for role: {role}")
            return Response(
                {"success": False, "message": f"No resume file found for role '{role}'"},
                status=status.HTTP_404_NOT_FOUND,
            )

        subject = SUBJECT_TEMPLATES[role]
        body = TEMPLATES[role]

        Thread(
            target=send_email_in_background,
            args=(
                email,
                role,
                subject,
                body,
                resume_path,
            ),
            daemon=True,
        ).start()

        return Response(
            {
                "success": True,
                "message": "Application queued successfully."
            },
            status=status.HTTP_200_OK,
        )
