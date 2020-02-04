import unittest
import os
import shutil
from pathlib import Path
from util.connectionHelper import connection_helper_factory, IoTConnectionHelper


class ModuleIntegrationTestCases(unittest.TestCase):
    def test_create_new_prov_assets_v2(self):
        api_version = 'v2'
        api_key_dev = 'bHq39E2eWO4WF8Y4kg3SC4shyERB3SAn2tyjZz4u'
        headers = {'Accept': 'application/json', 'x-api-key': api_key_dev}
        cert_store = f'{os.getcwd()}/unit_test/certificate_store'
        prov_base_url_dev = 'https://cfg.iot.dev.connectprint.cloud'
        config_url = f'{prov_base_url_dev}/{api_version}/configuration/?senderSoftwareVersion= &senderType= '

        options = {
            'certificate_store_path': cert_store,
            'amazon_root_ca_path': f'{cert_store}/amazonRootCA1.pem',
            'device_private_key_path': f'{cert_store}/devicePrivateKey.pem',
            'device_public_key_path': f'{cert_store}/devicePublicKey.pem',
            'device_cert_path': f'{cert_store}/deviceCert.cert',
            'client_id_file_path': f'{cert_store}/ClientID.txt',
            'headers': headers,
            'config_url': config_url,
            'body': None,
        }

        helper = connection_helper_factory(options)
        dirpath = Path(cert_store)
        if dirpath.exists() and dirpath.is_dir():
            shutil.rmtree(dirpath)
        res = helper.establish_connection()
        self.assertEqual(res['alreadyConnected'], False)

    def test_reuse_existing_assets(self):
        api_version = 'v2'
        api_key_dev = 'bHq39E2eWO4WF8Y4kg3SC4shyERB3SAn2tyjZz4u'
        headers = {'Accept': 'application/json', 'x-api-key': api_key_dev}
        cert_store = f'{os.getcwd()}/unit_test/certificate_store'
        prov_base_url_dev = 'https://cfg.iot.dev.connectprint.cloud'
        config_url = f'{prov_base_url_dev}/{api_version}/configuration/?senderSoftwareVersion= &senderType= '

        options = {
            'certificate_store_path': cert_store,
            'amazon_root_ca_path': f'{cert_store}/amazonRootCA1.pem',
            'device_private_key_path': f'{cert_store}/devicePrivateKey.pem',
            'device_public_key_path': f'{cert_store}/devicePublicKey.pem',
            'device_cert_path': f'{cert_store}/deviceCert.cert',
            'client_id_file_path': f'{cert_store}/ClientID.txt',
            'headers': headers,
            'config_url': config_url,
            'body': None,
        }

        helper = connection_helper_factory(options)
        assets_exists = helper.check_certificate()
        res = helper.establish_connection()
        if assets_exists:
            self.assertEqual(res['alreadyConnected'], True)
        else:
            self.assertEqual(res['alreadyConnected'], False)


class ConnectionHelperTest(unittest.TestCase):
    base_path = f'{os.getcwd()}/mockStore'
    certificate_store_path = f"{base_path}/cert_store_mock"
    amazon_root_ca_path = f"{base_path}/root_ca_mock.pem"
    device_private_key_path = f"{base_path}/device_private_key.pem"
    device_public_key_path = f"{base_path}/device_public_key.pem"
    device_cert_path = f"{base_path}/device_cert_path"
    client_id_file_path = f"{base_path}/client_id_path",

    def setUp(self) -> None:
        options = {
            'certificate_store_path': ConnectionHelperTest.certificate_store_path,
            'amazon_root_ca_path': ConnectionHelperTest.amazon_root_ca_path,
            'device_private_key_path': ConnectionHelperTest.device_private_key_path,
            'device_public_key_path': ConnectionHelperTest.device_public_key_path,
            'device_cert_path': ConnectionHelperTest.device_cert_path,
            'client_id_file_path': ConnectionHelperTest.client_id_file_path,
            'headers': {"Mocked": "headers"},
            'config_url': "config_url_mock",
            'body': {"Mocked": "body"},
        }
        self.con_helper = IoTConnectionHelper(options)

    def test_instance(self):
        self.assertIsInstance(self.con_helper, IoTConnectionHelper)

    def test_check_certificate_negative(self):
        res = self.con_helper.check_certificate()
        self.assertEqual(res, False)


if __name__ == '__main__':
    unittest.main()
