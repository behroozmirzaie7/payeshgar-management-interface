from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from inspecting import serializers, models, tasks


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

    def post(self, request, *args, **kwargs):
        results = request.data
        force_validate = request.GET.get('validate') == "1"
        if force_validate:
            serializer = serializers.CreateHTTPInspectionResultSerializer(data=results, many=True)
            serializer.is_valid(raise_exception=True)
        tasks.process_results(results)
        return Response({}, status=200)  # TODO: an empty response
