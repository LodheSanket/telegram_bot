from rest_framework import serializers

from services.resume_mapper import VALID_ROLES


class ApplyRequestSerializer(serializers.Serializer):
    """
    Validates the body of POST /api/apply/. EmailField handles the
    email format check, and ChoiceField only accepts roles that exist
    in services.resume_mapper.VALID_ROLES, so an unknown role gets
    rejected here before the view does anything else with it.
    """

    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=VALID_ROLES)
