from django.utils.functional import SimpleLazyObject
from rest_framework import mixins
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, UpdateAPIView, \
    CreateAPIView, GenericAPIView
from ipware import get_client_ip
from monitoring import models, serializers


class AgentListCreateView(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          GenericAPIView):
    serializer_class = serializers.AgentSerializer
    queryset = SimpleLazyObject(lambda: models.Agent.objects.all())
    _agent_object = None

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_object(self):
        if self._agent_object is None:
            self._agent_object = models.Agent.objects.filter(ip=self._get_client_ip_address()).first()
        return self._agent_object

    def post(self, request, *args, **kwargs):
        agent = self.get_object()
        if agent is None:
            return self.create(request, *args, **kwargs)
        return self.update(request, *args, **kwargs)

    def _get_client_ip_address(self):
        return get_client_ip(self.request)[0]

    def perform_create(self, serializer):
        return serializer.save(ip=self._get_client_ip_address())


class AgentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.AgentSerializer
    queryset = SimpleLazyObject(lambda: models.Agent.objects.all())
    lookup_url_kwarg = "agent_ip"


class EndpointListCreateView(ListCreateAPIView):
    serializer_class = serializers.EndpointSerializer
    queryset = SimpleLazyObject(
        lambda: models.Endpoint.objects.prefetch_related('http_details', 'monitoring_policy').all()
    )


class EndpointDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.EndpointSerializer
    queryset = SimpleLazyObject(lambda: models.Endpoint.objects.all())
    lookup_url_kwarg = "endpoint_uuid"
