from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from inspecting import models

from datetime import datetime, timedelta


class InspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Inspection
        exclude = []


class InspectionFilteringSerializer(serializers.Serializer):
    after = serializers.DateTimeField(required=False, default=None)
    before = serializers.DateTimeField(required=False, default=None)
    groups = serializers.ListField(required=False, default=list)

    def validate(self, attrs):
        default_period = timedelta(minutes=5)
        now = datetime.now()
        result = dict(
            before=attrs.get('before'),
            after=attrs.get('after'),
            groups=attrs.get('groups'),
        )
        if result['after'] is None and result['before'] is None:
            result['after'], result['before'] = now, now + default_period
        if result['after'] is None and result['before'] is not None:
            result['after'] = result['before'] - default_period
        if result['before'] is None and result['after'] is not None:
            result['before'] = result['after'] + default_period
        if result['after'] > result['before']:
            raise ValidationError("after should be less than or equal to before")
        return result


class CreateHTTPInspectionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HTTPInspectionResult
        fields = ['inspection', 'connection_status', 'status_code', 'response_time', 'byte_received']
