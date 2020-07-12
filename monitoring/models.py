import uuid

from django.db import models
from django.utils import timezone


class Group(models.Model):
    """
    Group Model: means of categorizing agents
        Primary key is a slug-like, URL friendly and Human readable string called name which will be used to identify
        each group.
        Agents will use this identifier in their config files.

    """
    name = models.SlugField(verbose_name="Name", primary_key=True, max_length=64)

    @property
    def endpoints(self):
        return Endpoint.objects.filter(monitoring_policy__groups=self)

    def __str__(self):
        return f"Group: {self.name}"


class Agent(models.Model):
    """
    Agent Model:

        Primary key is agent IP address, because this design considered agent IP address as it's identity.
        Name is a human-readable name for agent to be used in reports
        country is the country code according to ISO 3166-1 alpha-3 where agent's server is located.
        last_activity is the datetime of the last time server received a valid request from this agent,
        List of agents will be ordered by recent active agents by defaults
    """
    ip = models.CharField(verbose_name="IP Address", primary_key=True, max_length=15)
    name = models.CharField(verbose_name="Agent name", max_length=64)
    country = models.CharField(verbose_name="Country code", max_length=3, null=True)
    groups = models.ManyToManyField(Group, related_name="agents")
    last_activity = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Agent: {self.name} located at {self.country} IP={self.ip}"

    class Meta:
        ordering = ("-last_activity",)


class Endpoint(models.Model):
    """
    Endpoint Model:

        Primary key is an auto-generated UUID, UUID has been chosen to prevent accessing endpoints sequentially
        name is a unique url-friendly human-readable string to be used in URLs instead of ugly UUIDs
        List of endpoints will be ordered by their creation date by default

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.SlugField(verbose_name="Endpoint name", unique=True, help_text="Human readable slug for Endpoint")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"Endpoint: {self.name}"

    class Meta:
        ordering = ("-created_at",)


class HTTPEndpointDetail(models.Model):
    """
    HTTP details of Endpoint:
        Endpoint model did not specified type of the service intentionally, details of the endpoint has been separated
        in order to allow the design to support protocols other than HTTP in the future.
        each HTTP endpoint will have a one to one relationship with an HTTPEndpointDetail.

        hostname and port provide the address of the Endpoint
        path, port and tls are details of HTTP Endpoints
        maximum_expected_timeout indicates how much agent should wait for this endpoint to respond before it consider
        endpoint problematic.

    """
    endpoint = models.OneToOneField(Endpoint, on_delete=models.CASCADE, related_name="http_details")
    hostname = models.CharField(max_length=64, verbose_name="Hostname")
    port = models.CharField(max_length=5, verbose_name="Port")

    path = models.CharField(max_length=128, verbose_name="URL Path")
    method_name = models.CharField(max_length=8, verbose_name="HTTP Method name", choices=[
        ("GET", "GET"),
        ("POST", "POST")
    ])
    tls = models.BooleanField(default=True)
    maximum_expected_timeout = models.IntegerField(default=30000)

    def __str__(self):
        return f"HTTP Endpoint Detail: {'https' if self.tls else 'http'}{self.hostname}:{self.port} at {self.path}"


class MonitoringPolicy(models.Model):
    """
    Policy of monitoring: describe how system should monitor a specific Endpoint
    When it comes to monitoring a service, there are some details that are not relevant to the service itself, but they
    are required for monitoring.

    """
    endpoint = models.OneToOneField(Endpoint, on_delete=models.CASCADE, related_name="monitoring_policy")
    interval = models.PositiveIntegerField(default=30, verbose_name="Interval in seconds")
    groups = models.ManyToManyField(Group, related_name="+")

    def __str__(self):
        return f"Monitoring Policy: Monitoring {self.endpoint_id} every {self.interval} second(s) "
