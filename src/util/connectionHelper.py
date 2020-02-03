import json
import os
from os import path

import requests

from .log import get_logger

logger = get_logger(__name__)


def connection_helper_factory(options=None):

    base_url = os.getenv('base_url')
    auth_token = os.getenv('auth_token')
    api_version = os.getenv('api_version')
    config_url_path = 'configuration'
    base_path = f'{os.getcwd()}'
    certificate_store_path = f'{base_path}/certificate_store'
    amazon_root_ca_path = f'{certificate_store_path}/amazonRootCA1.pem'
    device_private_key_path = f'{certificate_store_path}/devicePrivateKey.pem'
    device_public_key_path = f'{certificate_store_path}/devicePublicKey.pem'
    device_cert_path = f'{certificate_store_path}/deviceCert.cert'
    client_id_file_path = f'{certificate_store_path}/ClientID.txt'
    org_id_file_path = f'{certificate_store_path}/OrgID.txt'

    headers_v3 = {'Accept': 'application/json', 'Authorization': f'Bearer {auth_token}'}
    config_url_v3 = f'{base_url}/{api_version}/{config_url_path}'

    if not options:
        options = {
            'certificate_store_path': certificate_store_path,
            'amazon_root_ca_path': amazon_root_ca_path,
            'device_private_key_path': device_private_key_path,
            'device_public_key_path': device_public_key_path,
            'device_cert_path': device_cert_path,
            'client_id_file_path': client_id_file_path,
            'org_id_file_path': org_id_file_path,
            'headers': headers_v3,
            'config_url': config_url_v3,
            'body': None,
        }
    return ConnectionHelper(options)


class IoTConnectionException(Exception):
    def __init__(self, message="IoT Connection failed", status_code=500, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class ConnectionHelper:
    def __init__(self, options):
        self.body = options.get('body')
        self.client_id_file_path = options.get('client_id_file_path')
        self.org_id_file_path = options.get('org_id_file_path')
        self.device_cert_path = options.get('device_cert_path')
        self.device_public_key_path = options.get('device_public_key_path')
        self.amazon_root_ca_path = options.get('amazon_root_ca_path')
        self.headers = options.get('headers')
        self.config_url = options.get('config_url')
        self.certificate_store_path = options.get('certificate_store_path')
        self.device_private_key_path = options.get('device_private_key_path')

    # Check whether device already have certificate
    def check_certificate(self):
        file = self.device_private_key_path
        path_exists = path.exists(file)
        return path_exists

    # Already Connected get the clientID
    @staticmethod
    def get_file_content(file):
        if str(path.exists('file')):
            with open(file) as readBuffer:
                client_id = str(readBuffer.read())
        else:
            client_id = None
        return client_id

    # write the certificate data to the files
    def write_data_file(self, file, data):
        try:
            if not os.path.exists(self.certificate_store_path):
                os.makedirs(self.certificate_store_path)
            file_handler = open(file, 'w')
            file_handler.write(data)  # str() converts to string
            file_handler.close()
        except Exception as err:
            message = f'file: {file} with data: {data} cannot be stored on disk'
            raise IoTConnectionException(message=message, details=err)

    # call the configuration API and get data
    def get_configuration(self):
        response = requests.get(self.config_url, headers=self.headers)
        if response.status_code == 200:
            content = json.loads(response.content.decode('utf-8'))
            certificate_data = content['connectivity']['serverRootCA']
            self.write_data_file(self.amazon_root_ca_path, certificate_data)
            logger.info('configuration successfully loaded')
            return content
        else:
            raise Exception('configuration api call not successful')

    # call the provisioning API and get data
    def get_provisioning(self, prov_api_url):
        logger.info('Starting provisioning...')
        response = requests.post(prov_api_url, headers=self.headers, data=self.body)
        if response.status_code == 200:
            logger.debug(response.status_code)
            content = json.loads(response.content.decode('utf-8'))
            device_private_key_data = content['devicePrivateKey']
            self.write_data_file(self.device_private_key_path, device_private_key_data)
            device_public_key_data = content['devicePublicKey']
            self.write_data_file(self.device_public_key_path, device_public_key_data)
            device_cert_data = content['deviceCert']
            self.write_data_file(self.device_cert_path, device_cert_data)
            client_id_data = content['clientId']
            self.write_data_file(self.client_id_file_path, client_id_data)
            org_id_data = content['orgId']
            self.write_data_file(self.org_id_file_path, org_id_data)
            logger.info('Provisioning API data connection successful, Certificate downloaded with new ClientID')
            return content
        else:
            raise IoTConnectionException(message='provisioning api call not successful')

    # Build the response for the demo_client
    def establish_connection(self):
        provisioning = False
        try:
            logger.info('Start establishing connection...')
            config = self.get_configuration()
            response = {**config}
            already_connected = self.check_certificate()
            if already_connected:
                response.update({'alreadyConnected': True})
                existing_client_id = ConnectionHelper.get_file_content(self.client_id_file_path)
                response.update({'clientId': existing_client_id})
                existing_org_id = ConnectionHelper.get_file_content(self.org_id_file_path)
                response.update({'orgId': existing_org_id})
                logger.info('This device is already provisioned')
            else:
                response.update({'alreadyConnected': False})
                logger.info('New demo_client Connection Started')
                prov_api_url = config['provisioning']['provisioningURL']
                prov_res = self.get_provisioning(prov_api_url)
                response.update(**prov_res)

            response.update({'device_private_key_path': self.device_private_key_path})
            response.update({'device_cert_path': self.device_cert_path})
            response.update({'amazon_root_ca_path': self.amazon_root_ca_path})
            return response
        except IoTConnectionException as err:
            raise err
        except Exception as err:
            raise IoTConnectionException(details=err)

