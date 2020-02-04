import json
import os
from os import path

import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from .log import get_logger

logger = get_logger(__name__)

COUNTRY_NAME = 'DE'
STATE = 'Berlin'
LOCALITY_NAME = 'Berlin'
ORGANIZATION_NAME = 'Heidelberger Druckmaschinen AG'
COMMON_NAME = 'Referenz-Client'
CERTIFICATE_VALIDITY_IN_DAYS = 720


def connection_helper_factory(options=None):
    base_url = os.getenv('base_url')
    auth_token = os.getenv('auth_token')
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
    config_url_v3 = f'{base_url}/v3/{config_url_path}'

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
            'config_url': config_url_v3
        }
    return IoTConnectionHelper(options)


class IoTConnectionException(Exception):
    def __init__(self, message="IoT Connection failed", status_code=500, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class IoTConnectionHelper:
    def __init__(self, options):
        self.client_id_file_path = options.get('client_id_file_path')
        self.org_id_file_path = options.get('org_id_file_path')
        self.device_cert_path = options.get('device_cert_path')
        self.device_public_key_path = options.get('device_public_key_path')
        self.amazon_root_ca_path = options.get('amazon_root_ca_path')
        self.headers = options.get('headers')
        self.config_url = options.get('config_url')
        self.certificate_store_path = options.get('certificate_store_path')
        self.device_private_key_path = options.get('device_private_key_path')
        self.device_pri_key = None
        self.device_pub_key = None

    def _check_needed_files(self):
        """Check if the needed files for mqtt connection are present"""

        files_to_check = [self.device_private_key_path, self.device_public_key_path, self.client_id_file_path,
                          self.org_id_file_path, self.device_cert_path]

        is_complete = True
        for f in files_to_check:
            is_there = path.exists(f)
            if not is_there:
                is_complete = False
        return is_complete

    @staticmethod
    def get_file_as_string(file):
        """"Load file as string"""
        if str(path.exists('file')):
            with open(file) as readBuffer:
                data = str(readBuffer.read())
        else:
            return None
        return data

    def _add_file_to_certificate_store(self, file, data):
        """Writes string to file"""
        try:
            if not os.path.exists(self.certificate_store_path):
                os.makedirs(self.certificate_store_path)
            file_handler = open(file, 'w')
            file_handler.write(data)
            file_handler.close()
        except Exception as err:
            message = f'file: {file} with data: {data} cannot be stored on disk'
            raise IoTConnectionException(message=message, details=err)

    def get_configuration(self):
        """call the configuration API and get config data"""
        response = requests.get(self.config_url, headers=self.headers)
        if response.status_code == 200:
            content = json.loads(response.content.decode('utf-8'))
            certificate_data = content['connectivity']['serverRootCA']
            self._add_file_to_certificate_store(self.amazon_root_ca_path, certificate_data)
            logger.info('configuration successfully loaded')
            return content
        else:
            raise Exception('configuration api call not successful')

    # call the provisioning API and get data
    def get_provisioning(self, prov_api_url):
        """call the provisioning API and get provisioning data"""
        logger.info('Starting provisioning...')
        response = requests.post(prov_api_url, headers=self.headers, data=self._build_provisioning_body())
        if response.status_code == 200:
            logger.info('Storing keys...')
            self._store_keys()
            content = json.loads(response.content.decode('utf-8'))
            logger.info('Storing device cert...')
            device_cert_data = content['deviceCert']
            self._add_file_to_certificate_store(self.device_cert_path, device_cert_data)
            logger.info('Storing client id...')
            client_id_data = content['clientId']
            self._add_file_to_certificate_store(self.client_id_file_path, client_id_data)
            logger.info('Storing org id...')
            org_id_data = content['orgId']
            self._add_file_to_certificate_store(self.org_id_file_path, org_id_data)
            logger.info('Provisioning API data connection successful, Certificate downloaded with new ClientID')
            return content
        else:
            raise IoTConnectionException(message='provisioning api call not successful')

    def establish_connection(self):
        """providing connection details"""
        try:
            logger.info('Start establishing connection...')
            config = self.get_configuration()
            response = {**config}
            needed_files_complete = self._check_needed_files()
            if needed_files_complete:
                response.update({'already_provisioned': True})
                existing_client_id = IoTConnectionHelper.get_file_as_string(self.client_id_file_path)
                response.update({'clientId': existing_client_id})
                existing_org_id = IoTConnectionHelper.get_file_as_string(self.org_id_file_path)
                response.update({'orgId': existing_org_id})
                logger.info('This device is already provisioned')
            else:
                response.update({'already_provisioned': False})
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

    def _build_provisioning_body(self):
        """Provide body payload for provisioning request"""
        csr_pem = self._create_csr()
        return json.dumps({"certificateSigningRequest": csr_pem.decode('utf-8'), })

    def _create_csr(self):
        """Creates a csr and signing it with device private key"""
        self._create_keys()

        csr_issuer = x509.Name([x509.NameAttribute(NameOID.COUNTRY_NAME, COUNTRY_NAME),
                                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, STATE),
                                x509.NameAttribute(NameOID.LOCALITY_NAME, LOCALITY_NAME),
                                x509.NameAttribute(NameOID.COMMON_NAME, COMMON_NAME)])

        csr = x509.CertificateSigningRequestBuilder().subject_name(csr_issuer).sign(self.device_pri_key,
                                                                                    hashes.SHA256(),
                                                                                    default_backend())
        return csr.public_bytes(encoding=serialization.Encoding.PEM)

    def _create_keys(self):
        """Creates RSA private and public key"""
        self.device_pri_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        self.device_pub_key = self.device_pri_key.public_key()

    def _store_keys(self):
        """Stores the keys in the certificate store"""
        device_pri_key_pem = self.device_pri_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        device_pub_key_pem = self.device_pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        self._add_file_to_certificate_store(self.device_private_key_path, device_pri_key_pem.decode('utf-8'))
        self._add_file_to_certificate_store(self.device_public_key_path, device_pub_key_pem.decode('utf-8'))
