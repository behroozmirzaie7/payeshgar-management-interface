import uuid

from django.db import models

from monitoring import models as monitoring_models


class Inspection(models.Model):
    """
    Inspection Model:
    describe a specific inspection of a specific endpoint which happened (or will happen) in a specific time
    Each Inspection could have zero, one or more corresponding HTTPInspectionResult objects.

    Primary Key is a UUID to prevent sequentially traversing list of inspections.
    timestamp is the point in time where inspection happened(or will be happen)

    List of inspection will be ordered by timestamp by default.

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    timestamp = models.DateTimeField()
    endpoint = models.ForeignKey(monitoring_models.Endpoint, on_delete=models.CASCADE, related_name='inspections')

    class Meta:
        ordering = ('timestamp',)
        unique_together = [
            ("endpoint", "timestamp")
        ]


class HTTPInspectionResult(models.Model):
    """
    HTTP Inspection Result Model:
    Keep the result of an HTTP Inspection, it uses a UUID to prevent sequentially traversing list of results.

    agent and agent_ip fields are responsible to keep reference to the agent who submit this specific result

    connection_status field will be:
        - SUCCEED: if the agent managed to received a valid HTTP response.
        - TIMED-OUT: if the agent didn't received a valid HTTP response because of a timeout error.
        - CONN-FAILED: if the agent didn't received a valid HTTP response for any reason other than timeout.
    status_code field will contain the response status_code, if there was a response otherwise it will be null
    response_time field will contain the whole time it took for agent to receive a response since it opened the socket,
    if there was a successful connection.
    byte_received field will contain the size of the response if there was a response otherwise it will be null .
    submitted_at field will contain the time where server received the result from the agent
    list of results will be sorted by result submit time by default

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name="http_results")

    agent = models.ForeignKey(monitoring_models.Agent, on_delete=models.SET_NULL, null=True)
    agent_ip = models.CharField(max_length=32)

    # Result:
    connection_status = models.CharField(max_length=16, choices=[
        ("SUCCEED", "SUCCEED",),
        ("CONN-FAILED", "CONN-FAILED",),
        ("TIMED-OUT", "TIMED-OUT",)
    ])
    status_code = models.CharField(max_length=4, null=True)
    response_time = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    byte_received = models.PositiveIntegerField(null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ("inspection", "agent_ip")
        ]
        ordering = ("submitted_at",)
