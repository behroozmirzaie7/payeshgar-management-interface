import json
import random
from datetime import timedelta, datetime

from rest_framework.test import APITestCase
from inspecting import models
from monitoring import models as monitoring_models
from monitoring.models import Agent


class InspectionTestingMixin:
    def create_endpoint(self, group_names):
        sample_endpoint = monitoring_models.Endpoint.objects.create(name=f'endpoint_{random.randint(1, 1000)}')
        groups = []
        for group_name in group_names:
            groups.append(monitoring_models.Group.objects.create(
                name=group_name
            ))
        policy = monitoring_models.MonitoringPolicy.objects.create(endpoint=sample_endpoint)
        policy.groups.add(*groups)
        return sample_endpoint

    def _create_sample_inspection(self, count=10, start_from=None, interval=timedelta(seconds=30), endpoint=None):
        cur = start_from or datetime.now()
        for i in range(count):
            models.Inspection.objects.create(endpoint=endpoint or self.sample_endpoint, timestamp=cur)
            cur += interval


class ReadingInspectionsTestCase(APITestCase, InspectionTestingMixin):

    def setUp(self):
        self.sample_groups = ["asia", "europe", "china", "us"]
        self.sample_endpoint = self.create_endpoint(group_names=self.sample_groups)

    def test_list_all_inspections_sunny_day(self):
        self._create_sample_inspection()
        response = self.client.get("/api/v1/inspecting/inspections")
        inspections = response.json()

        self.assertEquals(response.status_code, 200)

        self.assertEquals(len(inspections), 9)

    def test_list_all_inspections_for_specific_time_period(self):
        # Expectations:
        interval = 5
        time_window = 31
        number_of_points = time_window // interval

        # Arrange
        specific_time_period = datetime(2020, 7, 7, 15, 30, 40)  # some random point in time
        self._create_sample_inspection(start_from=specific_time_period, interval=timedelta(seconds=interval))

        filters = dict(
            after=specific_time_period,
            before=specific_time_period + timedelta(seconds=time_window)
        )
        response = self.client.get("/api/v1/inspecting/inspections", data=filters)

        inspections = response.json()
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(inspections), number_of_points)

    def test_list_all_inspections_for_specific_groups(self):
        endpoint = self.create_endpoint(["foo", "bar"])
        self._create_sample_inspection()
        self._create_sample_inspection(endpoint=endpoint, count=5)

        expected_count = 4
        expected_endpoint_id = str(endpoint.id)

        filters = dict(
            groups=["foo", "bar"]
        )
        response = self.client.get("/api/v1/inspecting/inspections", data=filters)

        inspections = response.json()

        self.assertEquals(response.status_code, 200)

        # All of them belong to our expected endpoint:
        self.assertTrue(all([i['endpoint'] == expected_endpoint_id for i in inspections]))

        # number of distinct objects are as expected
        distinct_result_count = len(set([i['id'] for i in inspections]))
        self.assertEquals(distinct_result_count, expected_count)


class SubmitInspectionResultTestCase(APITestCase, InspectionTestingMixin):

    def setUp(self):
        self.sample_groups = ["asia", "europe", "china", "us"]
        self.sample_endpoint = self.create_endpoint(group_names=self.sample_groups)
        self.agent = Agent.objects.create(ip="127.0.0.1", name="Local", country="NWR")

    def test_submit_a_single_result_sunny_day(self):
        self._create_sample_inspection()
        sample_inspection_id = models.Inspection.objects.first().id

        body = json.dumps(
            [
                {
                    'inspection': str(sample_inspection_id),
                    'connection_status': "SUCCEED",
                    'status_code': 401,
                    'response_time': 0.128,
                    'byte_received': 2048
                }
            ]
        )
        response = self.client.post("/api/v1/inspecting/inspection-results", data=body, content_type='application/json')

        self.assertEquals(response.status_code, 200)

    def test_submit_a_single_invaid_result_without_validation_flag_should_return_200(self):
        self._create_sample_inspection()
        sample_inspection_id = models.Inspection.objects.first().id

        body = json.dumps(
            [
                {
                    'inspection': str(sample_inspection_id),
                    'connection_status': "SUCCEED",
                    'status_code': "INVALID",
                    'response_time': "INVALID VALUE",
                    'byte_received': "INVALID VALUE"
                }
            ]
        )
        response = self.client.post("/api/v1/inspecting/inspection-results", data=body, content_type='application/json')

        self.assertEquals(response.status_code, 200)

    def test_submit_a_single_invaid_result_with_validation_flag_should_return_400_and_errors(self):
        self._create_sample_inspection()
        sample_inspection_id = models.Inspection.objects.first().id

        body = json.dumps(
            [
                {
                    'inspection': str(sample_inspection_id),
                    'connection_status': "SUCCEED",
                    'status_code': "INVALID",
                    'response_time': "INVALID VALUE",
                    'byte_received': "INVALID VALUE"
                }
            ]
        )
        response = self.client.post("/api/v1/inspecting/inspection-results?validate=1", data=body,
                                    content_type='application/json')

        self.assertEquals(response.status_code, 400)

    def test_submit_a_single_valid_result_with_an_unknown_ip(self):
        self.agent.delete()
        self._create_sample_inspection()
        sample_inspection_id = models.Inspection.objects.first().id

        body = json.dumps(
            [
                {
                    'inspection': str(sample_inspection_id),
                    'connection_status': "SUCCEED",
                    'status_code': 401,
                    'response_time': 0.128,
                    'byte_received': 2048
                }
            ]
        )
        response = self.client.post("/api/v1/inspecting/inspection-results?validate=1", data=body,
                                    content_type='application/json')

        self.assertEquals(response.status_code, 401)

