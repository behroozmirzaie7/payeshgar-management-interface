from django.utils.functional import SimpleLazyObject
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from monitoring import models, serializers


class AgentListCreateView(ListCreateAPIView):
    serializer_class = serializers.AgentSerializer
    queryset = SimpleLazyObject(lambda: models.Agent.objects.all())


class AgentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.AgentSerializer
    queryset = SimpleLazyObject(lambda: models.Agent.objects.all())
    lookup_url_kwarg = "agent_name"


class EndpointListCreateView(ListCreateAPIView):
    serializer_class = serializers.EndpointSerializer
    queryset = SimpleLazyObject(
        lambda: models.Endpoint.objects.prefetch_related('http_details', 'monitoring_policy').all()
    )


class EndpointDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.EndpointSerializer
    queryset = SimpleLazyObject(lambda: models.Endpoint.objects.all())
    lookup_url_kwarg = "endpoint_uuid"
