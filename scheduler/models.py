import uuid

from django.db import models
from django.utils import timezone

from monitoring import models as monitoring_models


class Inspection(models.Model):
    """
    a new object will created each time we start inspecting an endpoint by one or more agent
    an Inspection could have multiple InspectionTask, depend on the number of agents
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(monitoring_models.Endpoint, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, default="PENDING", choices=[
        ("PENDING", "PENDING"),
        ("FINISHED", "FINISHED")
    ])
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, default=None)
    took = models.PositiveIntegerField(null=True, default=None)

    def mark_as_finish(self, commit=True):
        self.status = "FINISHED"
        self.finished_at = timezone.now()
        self.took = round((self.finished_at - self.started_at).total_seconds(), 0)
        if commit:
            self.save()


class InspectionTask(models.Model):
    """
    a new object will created each time we ask an agent to inspect an endpoint
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name="tasks")
    agent = models.ForeignKey(monitoring_models.Agent, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, default="PENDING", choices=[
        ("PENDING", "PENDING"),
        ("SUCCEED", "SUCCEED"),
        ("FAILED", "FAILED"),
    ])
    error = models.TextField(default="")

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, default=None)
    took = models.PositiveIntegerField(null=True, default=None)

    @property
    def result(self):
        return self.http_result

    def mark_as_finish(self, error_message=None, commit=True):
        self.status = "SUCCEED" if error_message is None else "FAILED"
        self.error = error_message
        self.finished_at = timezone.now()
        self.took = round((self.finished_at - self.started_at).total_seconds(), 0)
        if commit:
            self.save()


class HTTPInspectionResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection_task = models.OneToOneField(InspectionTask, on_delete=models.CASCADE, related_name="http_result")
    successful_connection = models.BooleanField()
    status_code = models.CharField(max_length=4)
    dns_lookup_time = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    connect_time = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    response_time = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    byte_received = models.PositiveIntegerField(null=True)
