import random
from datetime import timedelta, datetime

from rest_framework.test import APITestCase
from inspecting import models
from monitoring import models as monitoring_models


class ReadingInspectionsTestCase(APITestCase):
    def setUp(self):
        self.sample_groups = ["asia", "europe", "china", "us"]
        self.sample_endpoint = self.create_endpoint(group_names=self.sample_groups)

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
