from django.db.models import Prefetch
from django.utils.functional import SimpleLazyObject
from rest_framework.generics import ListAPIView, RetrieveAPIView
from scheduler import serializers, models


class InspectionListAPIView(ListAPIView):
    serializer_class = serializers.MinimalInspectionSerializer
    queryset = SimpleLazyObject(
        lambda: models.Inspection.objects.prefetch_related(
            Prefetch('tasks', queryset=models.InspectionTask.objects.only('id', 'status', 'started_at')),
        ).all()
    )


class InspectionDetailAPIView(RetrieveAPIView):
    serializer_class = serializers.InspectionSerializer
    queryset = SimpleLazyObject(
        lambda: models.Inspection.objects.prefetch_related(
            'tasks', 'tasks__agent', 'tasks__http_result'
        ).all()
    )
    lookup_url_kwarg = 'inspection_uuid'
