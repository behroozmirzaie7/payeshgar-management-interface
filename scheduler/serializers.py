from rest_framework import serializers
from scheduler import models
from monitoring.serializers import AgentSerializer


class HTTPInspectionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HTTPInspectionResult
        exclude = ["inspection_task"]


class InspectionTaskSerializer(serializers.ModelSerializer):
    agent = AgentSerializer()
    result = HTTPInspectionResultSerializer()

    class Meta:
        model = models.InspectionTask
        exclude = ['inspection']


class InspectionTaskStatusSerializer(serializers.ModelSerializer):


    class Meta:
        model = models.InspectionTask
        fields = ['id', 'agent_id', 'status', 'started_at']


class InspectionSerializer(serializers.ModelSerializer):
    tasks = InspectionTaskSerializer(many=True)

    class Meta:
        model = models.Inspection
        exclude = ['endpoint']


class MinimalInspectionSerializer(serializers.ModelSerializer):
    tasks = InspectionTaskStatusSerializer(many=True)

    class Meta:
        model = models.Inspection
        exclude = ['endpoint']
