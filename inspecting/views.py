from datetime import datetime

from ipware import get_client_ip
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from inspecting import serializers, models, tasks
from monitoring.models import Agent


class InspectionListAPIView(ListAPIView):
    serializer_class = serializers.InspectionSerializer

    def _get_filtering(self):
        serializer = serializers.InspectionFilteringSerializer(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def get_queryset(self):
        filters = self._get_filtering()
        queryset = models.Inspection.objects.filter(
            timestamp__gt=filters['after'],
            timestamp__lt=filters['before'],
        ).select_related('endpoint', 'endpoint__monitoring_policy', )
        if len(filters['groups']) > 0:
            queryset = queryset.distinct().filter(endpoint__monitoring_policy__groups__in=filters['groups'])
        return queryset


class CreateInspectionResultsAPIView(APIView):
    model = models.HTTPInspectionResult

    def get_agent_ip(self):
        client_ip = get_client_ip(self.request)[0]
        agent = Agent.objects.filter(ip=client_ip).first()
        if agent is None:
            exc = ValidationError({"non_field_error": "IP Address is not recognized"})
            exc.status_code = 401
            raise exc
        return client_ip

    def _run_background_task(self, results):
        tasks.process_results(
            agent_ip=self.get_agent_ip(),
            submission_time=datetime.now(),
            results=results,
        )

    def post(self, request, *args, **kwargs):
        results = request.data
        force_validate = request.GET.get('validate') == "1"
        if force_validate:
            serializer = serializers.CreateHTTPInspectionResultSerializer(data=results, many=True)
            serializer.is_valid(raise_exception=True)
        self._run_background_task(results)
        return Response({}, status=200)  # TODO: an empty response
