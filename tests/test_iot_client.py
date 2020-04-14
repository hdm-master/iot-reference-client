import unittest
from unittest.mock import Mock, patch

from iot_assets.iot_client import IoTClientDetails, IoTClient


class IoTClientTests(unittest.TestCase):
    @patch("iot_assets.iot_client.paho")
    def setUp(self, paho_mock):
        self.iot_client_details = IoTClientDetails("mqttEndpointMock", 123, "deviceCertPathMock",
                                                   "devicePrivateKeyPathMock",
                                                   "amazonRootCaPathMock", "thingNameMock")
        self.iot = IoTClient(self.iot_client_details)

    def test_init(self):
        self.assertIsInstance(self.iot, IoTClient)

    @patch("iot_assets.iot_client.paho")
    def test_connect(self, paho_mock):
        client_mock = Mock()
        paho_mock.Client.return_value = client_mock
        iot_client = IoTClient(self.iot_client_details)
        err = False
        try:
            iot_client.connect(ssl_tunnel=False)
        except Exception:
            err = True

        self.assertEqual(err, False)
        client_mock.connect.assert_called_with(self.iot_client_details.mqtt_endpoint,
                                               self.iot_client_details.standard_port, keepalive=IoTClient.keep_alive)
