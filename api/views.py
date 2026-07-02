import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from services.email_service import send_application_email
from services.resume_mapper import get_resume_path
from services.templates import SUBJECT_TEMPLATES, TEMPLATES

from .authentication import APIKeyAuthentication
from .models import ApplicationHistory
from .serializers import ApplyRequestSerializer

logger = logging.getLogger("api")


class ApplyView(APIView):
    """
    Handles POST /api/apply/. This is the only endpoint the Telegram
    bot calls. Given an email and a role, it picks the matching resume
    and email template, sends the email, records the attempt in
    ApplicationHistory, and reports back whether it worked.
    """

    # authentication_classes = [APIKeyAuthentication]
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

        success, message = send_application_email(email, subject, body, resume_path)

        # Every attempt gets logged, whether it succeeded or not, so
        # there's a full history to look back on later.
        ApplicationHistory.objects.create(
            recipient_email=email,
            role=role,
            status="sent" if success else "failed",
        )

        if success:
            logger.info(f"Email sent to {email} for role {role}")
            return Response({"success": True, "message": "Application sent"}, status=status.HTTP_200_OK)

        logger.error(f"Email failed for {email}, role {role}: {message}")
        return Response(
            {"success": False, "message": message},
            status=status.HTTP_502_BAD_GATEWAY,
        )
