import re

from django.db.transaction import atomic
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


class HTTPEndpointDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HTTPEndpointDetail
        exclude = ["endpoint"]

    def validate_port(self, value: str):
        if not value.isnumeric():
            raise ValidationError("port should be an integer between 1-65535")
        return value


class EndpointSerializer(serializers.ModelSerializer):
    http_details = HTTPEndpointDetailSerializer()

    class Meta:
        model = models.Endpoint
        exclude = []

    def _create_or_update_http_detail(self, raw_data: dict, endpoint: models.Endpoint):
        current_http_detail = models.HTTPEndpointDetail.objects.filter(endpoint=endpoint).first()
        if current_http_detail is None:
            serializer = HTTPEndpointDetailSerializer(data=raw_data)
        else:
            serializer = HTTPEndpointDetailSerializer(instance=current_http_detail, data=raw_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(endpoint=endpoint)

    def create(self, validated_data):
        http_details = validated_data.pop('http_details', None)
        with atomic():
            instance = super(EndpointSerializer, self).create(validated_data)
            self._create_or_update_http_detail(raw_data=http_details, endpoint=instance)
        return instance

    def update(self, instance, validated_data):
        http_details = validated_data.pop('http_details', None)
        with atomic():
            instance = super(EndpointSerializer, self).update(instance, validated_data)
            if http_details is not None:
                self._create_or_update_http_detail(raw_data=http_details, endpoint=instance)
        return instance
