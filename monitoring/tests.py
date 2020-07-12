import json
from monitoring import models

from rest_framework.test import APITestCase


class AgentCreationTestCase(APITestCase):
    def setUp(self):
        self.groups = ["europe", "hetzner", "germany"]
        models.Group.objects.bulk_create(
            [models.Group(name=group) for group in self.groups]
        )

    def test_agent_is_introduce_itself_should_create_agent_record(self):
        body = dict(
            name="foo1",
            groups=self.groups,
            country="DEU",
        )
        response = self.client.post("/api/v1/monitoring/agents", data=json.dumps(body), content_type="application/json")

        self.assertEquals(response.status_code, 201)

    def test_agent_introducing_itself_multiple_time_is_ok(self):
        body = dict(
            name="foo_0",
            groups=self.groups,
            country="deu",
        )
        response = self.client.post("/api/v1/monitoring/agents", data=json.dumps(body), content_type="application/json")
        self.assertEquals(response.status_code, 201)

        for i in range(1, 10):
            name = f"foo_{i}"
            body = dict(
                name=name,
                groups=self.groups,
                country="deu",
            )
            response = self.client.post("/api/v1/monitoring/agents", data=json.dumps(body),
                                        content_type="application/json")
            data = json.loads(response.content.decode('utf8'))
            self.assertEquals(response.status_code, 200)
            self.assertEquals(data['name'], name)

    def test_agent_introducing_itself_with_invalid_country_code_is_not_ok(self):
        body = dict(
            name="foo",
            groups=self.groups,
            country="99u",
        )
        response = self.client.post("/api/v1/monitoring/agents", data=json.dumps(body), content_type="application/json")
        data = json.loads(response.content)
        self.assertIn('country', data)
        self.assertEquals(response.status_code, 400)


class ReadingAgentsTestCase(APITestCase):
    def setUp(self):
        self.groups = ["europe", "hetzner", "germany"]
        models.Group.objects.bulk_create(
            [models.Group(name=group) for group in self.groups]
        )
        body = dict(
            name="foo1",
            groups=self.groups,
            country="DEU",
        )
        response = self.client.post("/api/v1/monitoring/agents", data=json.dumps(body), content_type="application/json")

        self.assertEquals(response.status_code, 201)

    def test_get_details_of_an_agent(self):
        response = self.client.get("/api/v1/monitoring/agents/127.0.0.1")
        data = json.loads(response.content)
        self.assertEquals(response.status_code, 200)

    def test_get_list_of_agents(self):
        response = self.client.get("/api/v1/monitoring/agents")
        data = json.loads(response.content)
        self.assertEquals(response.status_code, 200)


class EndpointCreationTestCase(APITestCase):
    def setUp(self):
        self.groups = ["europe", "hetzner", "germany"]
        models.Group.objects.bulk_create(
            [models.Group(name=group) for group in self.groups]
        )

    def test_create_simple_http_endpoint_with_default_policy(self):
        testcase = {
            "http_details": {
                "hostname": "google.com",
                "path": "/",
                "port": "443",
                "method_name": "GET",
                "tls": True,
            },
            "name": "google-com-homepage"
        }
        response = self.client.post("/api/v1/monitoring/endpoints", data=json.dumps(testcase),
                                    content_type="application/json")
        print(response.content)
        self.assertEquals(response.status_code, 201)
        self.assertTrue(models.Endpoint.objects.all().exists())
        self.assertTrue(models.HTTPEndpointDetail.objects.all().exists())
        self.assertTrue(models.MonitoringPolicy.objects.all().exists())

    def test_create_simple_http_endpoint_with_non_default_policy(self):
        testcase = {
            "http_details": {
                "hostname": "google.com",
                "path": "/",
                "port": "443",
                "method_name": "GET",
                "tls": True,
            },
            "monitoring_policy": {
                "agent_selector": "",
                "interval": 300,
            },
            "name": "google-com-homepage",
            "description": "Google homepage",
            "active": True,
        }
        response = self.client.post(
            "/api/v1/monitoring/endpoints",
            data=json.dumps(testcase),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 201)
        self.assertTrue(models.Endpoint.objects.all().exists())
        self.assertTrue(models.HTTPEndpointDetail.objects.all().exists())
        self.assertTrue(models.MonitoringPolicy.objects.all().exists())

    def test_create_simple_http_endpoint_with_non_default_policy_without_interval(self):
        testcase = {
            "http_details": {
                "hostname": "google.com",
                "path": "/",
                "port": "443",
                "method_name": "GET",
                "tls": True,
            },
            "monitoring_policy": {
                "agent_selector": "",
            },
            "name": "google-com-homepage",
            "description": "Google homepage",
            "active": True,
        }
        response = self.client.post(
            "/api/v1/monitoring/endpoints",
            data=json.dumps(testcase),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 201)
        self.assertTrue(models.Endpoint.objects.all().exists())
        self.assertTrue(models.HTTPEndpointDetail.objects.all().exists())
        self.assertTrue(models.MonitoringPolicy.objects.all().exists())
        self.assertEquals(models.MonitoringPolicy.objects.all().first().interval, 30)

    def test_update_simple_http_endpoint(self):
        instance = models.Endpoint.objects.create(name='foo1')
        testcase = {
            "name": "foo2",
        }
        self.assertEquals(models.Endpoint.objects.get(id=instance.id).name, "foo1")
        response = self.client.patch(f"/api/v1/monitoring/endpoints/{instance.id}",
                                     data=json.dumps(testcase), content_type="application/json")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(models.Endpoint.objects.get(id=instance.id).name, "foo2")

    def test_update_port_in_a_http_endpoint(self):
        endpoint = models.Endpoint.objects.create(name='foo1')
        models.HTTPEndpointDetail.objects.create(
            **{'endpoint': endpoint,
               'hostname': "google.com",
               'port': "443",
               'tls': True,
               'method_name': "GET",
               'path': "/"})
        testcase = {
            "http_details": {
                "port": "8443"
            },
        }
        self.assertEqual(models.Endpoint.objects.get(id=endpoint.id).http_details.port, "443")
        response = self.client.patch(f"/api/v1/monitoring/endpoints/{endpoint.id}",
                                     data=json.dumps(testcase), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Endpoint.objects.get(id=endpoint.id).http_details.port, "8443")

    def test_update_port_in_a_http_endpoint_with_invalid_port(self):
        endpoint = models.Endpoint.objects.create(name='foo1')
        models.HTTPEndpointDetail.objects.create(
            **{'endpoint': endpoint,
               'hostname': "google.com",
               'port': "443",
               'tls': True,
               'method_name': "GET",
               'path': "/"})
        testcase = {
            "http_details": {
                "port": "abc"
            },
        }
        self.assertEqual(models.Endpoint.objects.get(id=endpoint.id).http_details.port, "443")
        response = self.client.patch(f"/api/v1/monitoring/endpoints/{endpoint.id}",
                                     data=json.dumps(testcase), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_update_port_in_a_http_endpoint_with_invalid_method_name(self):
        endpoint = models.Endpoint.objects.create(name='foo1')
        models.HTTPEndpointDetail.objects.create(
            **{'endpoint': endpoint,
               'hostname': "google.com",
               'port': "443",
               'tls': True,
               'method_name': "GET",
               'path': "/"})
        testcase = {
            "http_details": {
                "method_name": "abc"
            },
        }
        self.assertEqual(models.Endpoint.objects.get(id=endpoint.id).http_details.port, "443")
        response = self.client.patch(f"/api/v1/monitoring/endpoints/{endpoint.id}",
                                     data=json.dumps(testcase), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_update_interval_in_a_policy(self):
        endpoint = models.Endpoint.objects.create(name='foo1')
        models.HTTPEndpointDetail.objects.create(
            **{'endpoint': endpoint,
               'hostname': "google.com",
               'port': "443",
               'tls': True,
               'method_name': "GET",
               'path': "/"})
        models.MonitoringPolicy.objects.create(**{'endpoint': endpoint})

        testcase = {
            "monitoring_policy": {
                "interval": 49283487
            },
        }
        self.assertEqual(models.Endpoint.objects.get(id=endpoint.id).http_details.port, "443")
        response = self.client.patch(f"/api/v1/monitoring/endpoints/{endpoint.id}",
                                     data=json.dumps(testcase), content_type="application/json")
        self.assertEqual(response.status_code, 400)
