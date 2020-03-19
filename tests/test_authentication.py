import unittest
import uuid
from unittest.mock import patch, Mock, MagicMock

from onboarding.zaikio_manager import ZaikioManager


class AuthenticationUnitTest(unittest.TestCase):
    def test_positive_constructor(self):
        am = ZaikioManager('mock', 'mock', 'mock')
        self.assertIsInstance(am, ZaikioManager)

    @patch("onboarding.zaikio_manager.requests.post")
    def test_postive_authorize(self, post_mock):

        def post_response(url, headers):
            response_mock = Mock()
            response_mock.status_code = 200
            response_mock.json.return_value = {
                "device_code": "sampleDeviceCode",
                "user_code": "sampleUserCode",
                "verification_uri": "uri_to_verify",
                "verification_uri_complete": "uri_to_verify"
                                             "?code=sampleUserCode",
                "expires_in": 299,
                "interval": 5
            }
            return response_mock

        post_mock.side_effect = post_response
        am = ZaikioManager('mock', 'mock', 'mock')
        am._check_device_authorization = Mock(return_value='aaa.bbb.ccc')

        raised = False
        token = None
        try:
            token = am._authorize()
        except Exception as err:
            raised = True
        self.assertFalse(raised)
        self.assertIsNotNone(token)

    @patch("onboarding.zaikio_manager.requests.post")
    def test_positive_invalid_request(self, post_mock):
        def post_response(url, data):
            response_mock = Mock()
            response_mock.status_code = 404
            response_mock.json.return_value = {
                "error": "invalid_request"
            }
            return response_mock

        post_mock.side_effect = post_response
        am = ZaikioManager('mock', 'mock', 'mock')
        self.assertRaises(Exception, am._check_device_authorization, 1, "device_code")

    @patch("onboarding.zaikio_manager.requests.post")
    def test_positive_expired_token(self, post_mock):
        def post_response(url, data):
            response_mock = Mock()
            response_mock.status_code = 400
            response_mock.json.return_value = {
                "error": "expired_token"
            }
            return response_mock

        post_mock.side_effect = post_response
        am = ZaikioManager('mock', 'mock', 'mock')
        self.assertRaises(Exception, am._check_device_authorization, 1, "device_code")

    @patch("onboarding.zaikio_manager.requests.post")
    def test_positive_200_access_token(self, post_mock):
        def post_response_200(url, data):
            response_mock = MagicMock()
            response_mock.status_code = 200
            response_mock.json.return_value = {
                "access_token": "fakeToken"
            }
            return response_mock

        post_mock.side_effect = post_response_200
        am = ZaikioManager('mock', 'mock', 'mock')
        raised = False
        token = None
        try:
            token = am._check_device_authorization(1, "device_code")
        except Exception as err:
            raised = True
        self.assertFalse(raised)
        self.assertEqual(token, "fakeToken")


@unittest.skip('Integration tests. Should not run normally')
class AuthenticationIntegrationTest(unittest.TestCase):
    """This test will actually call the auth service. It is an integration test. They won't run when calling
     python -m unittest discover """

    def test_positive_authorization(self):
        am = ZaikioManager('600b71b7-b4cf-44ac-8c00-92283d50f9a5',
                           'https://directory.sandbox.zaikio.com', 'Org.prinect.onprem.rw,'
                                                                   'Org.directory.machines.rw')
        raised = False
        token = None
        try:
            token = am.run_device_auth_flow()
        except Exception:
            raised = True
        self.assertFalse(raised)
        self.assertIsInstance(token, str)

    def test_machine_onboarding(self):
        am = ZaikioManager('600b71b7-b4cf-44ac-8c00-92283d50f9a5',
                           'https://directory.sandbox.zaikio.com', 'Org.prinect.onprem.rw,'
                                                                   'Org.directory.machines.rw')
        raised = False
        try:
            token = am.run_device_auth_flow()
            am.onboard_machine(token, "demo_name", "demo_manufacturer", str(uuid.uuid1()), "digital_press")
        except Exception as err:
            raised = True
        self.assertFalse(raised)
