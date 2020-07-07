import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from monitoring import models


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Agent
        exclude = []

    def validate_url(self, value: str):
        if not value[0:5].lower().startswith("https"):
            raise ValidationError("Agent access URL must be HTTPS")
        return value

    def validate_namespace(self, value: str):
        pattern = r"^[a-z0-9_.]{0,64}$"
        value = value.lower()
        if not re.match(pattern, value):
            raise ValidationError(f"namespaces should match {pattern}")
        return value


class EndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Endpoint
        exclude = []
