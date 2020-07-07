import json
from monitoring import models

from rest_framework.test import APITestCase


class EndpointCreationTestCase(APITestCase):
    def test_create_simple_http_endpoint(self):
        testcase = {
            "http_details": {
                "hostname": "google.com",
                "path": "/",
                "port": "443",
                "method_name": "GET",
                "tls": True,
            },
            "name": "google-com-homepage",
            "description": "Google homepage",
            "active": True,
        }
        response = self.client.post("/api/v1/monitoring/endpoints", data=json.dumps(testcase),
                                    content_type="application/json")
        self.assertEquals(response.status_code, 201)
        self.assertTrue(models.Endpoint.objects.all().exists())
        self.assertTrue(models.HTTPEndpointDetail.objects.all().exists())


    def test_update_simple_http_endpoint(self):
        instance = models.Endpoint.objects.create(name='foo1')
        testcase = {
            "active": False,
        }
        self.assertTrue(models.Endpoint.objects.get(id=instance.id).active)
        response = self.client.patch(f"/api/v1/monitoring/endpoints/{instance.id}",
                                     data=json.dumps(testcase), content_type="application/json")
        self.assertEquals(response.status_code, 200)
        self.assertFalse(models.Endpoint.objects.get(id=instance.id).active)

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
