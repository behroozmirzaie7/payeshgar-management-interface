from django.db import models


class Agent(models.Model):
    """
    Each Agent instance holds require information to access an agent
    """
    name = models.SlugField(verbose_name="Agent ID", primary_key=True, help_text="Unique Human readable slug for agent")
    namespace = models.CharField(max_length=64, default="global", help_text="Examples: europe.germany.hetzner")
    url = models.URLField("Agent Access URL")
    token = models.CharField(max_length=128, )
    status = models.CharField(max_length=16, choices=[
        ("ACTIVE", "Active Agent"),
        ("INACTIVE", "Inactive Agent"),
    ])
    details = models.TextField(default="", help_text="last access information")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Agent: {self.name} located in {self.namespace} status is {self.status}"

    class Meta:
        index_together = [
            ("namespace",),
            ("status",),
            ("status", "namespace")
        ]


class Endpoint(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.SlugField(verbose_name="Endpoint name", db_index=True, help_text="Human readable slug for Endpoint")
    description = models.TextField(default="")
    active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"Endpoint: {self.name}"

    class Meta:
        ordering = ("-created_at",)


class HTTPEndpointDetail(models.Model):
    endpoint = models.OneToOneField(Endpoint, on_delete=models.CASCADE, related_name="http_details")
    hostname = models.CharField(max_length=64, verbose_name="Hostname")
    path = models.CharField(max_length=128, verbose_name="URL Path")
    port = models.CharField(max_length=5, verbose_name="Port")
    method_name = models.CharField(max_length=8, verbose_name="HTTP Method name", choices=[
        ("GET", "GET"),
        ("POST", "POST")
    ])

    tls = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"HTTP Endpoint Detail: {'https' if self.tls else 'http'}{self.hostname}:{self.port} at {self.path}"


class MonitoringPolicy(models.Model):
    endpoint = models.OneToOneField(Endpoint, on_delete=models.CASCADE, related_name="monitoring_policy")
    agent_selector = models.CharField(max_length=64, help_text="Examples: europe.* or hetzner.* depending on how you "
                                                               "defined your agents namespaces")
    interval = models.IntegerField(default=15, verbose_name="Interval in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Monitoring Policy: Monitoring {self.endpoint_id} every {self.interval} second(s) " \
               f"using {self.agent_selector}"
