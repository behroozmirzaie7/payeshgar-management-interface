import json

from rest_framework.test import APITestCase
from inspecting import models
from monitoring import models as monitoring_models


class ReadingInspectionsTestCase(APITestCase):
    def setUp(self):
        self.sample_endpoint = monitoring_models.Endpoint.objects.create(name='endpoint1')
        self.agents = []
        for region in ["asia", "europe", "china", "us"]:
            self.agents.append(monitoring_models.Agent.objects.create(
                name=region,
                namespace=region,
                url=f"https://{region}.payeshgar.mycompany.com",
                token="Booh!",
                status="Active"
            ))
        self.inspection = models.Inspection.objects.create(endpoint=self.sample_endpoint)
        self.tasks = []
        for agent in self.agents:
            self.tasks.append(models.InspectionTask.objects.create(
                inspection=self.inspection,
                agent=agent,
                status="PENDING"
            ))

    def test_list_all_inspections(self):
        response = self.client.get("/api/v1/inspecting/inspections", )
        self.assertEquals(response.status_code, 200)
        result = response.json()
        self.assertEquals(len(result), 1)
        first_inspection = result[0]
        self.assertEquals(len(first_inspection['tasks']), 4)

    def test_list_all_inspections2(self):
        response = self.client.get(f"/api/v1/inspecting/inspections/{self.inspection.id}", )
        self.assertEquals(response.status_code, 200)
        result = response.json()
        self.assertEquals(len(result['tasks']), 4)
