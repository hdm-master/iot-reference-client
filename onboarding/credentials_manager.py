import os
from os import path

import logging
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from typing import Dict

logger = logging.getLogger(__name__)

COUNTRY_NAME = 'DE'
STATE = 'Berlin'
LOCALITY_NAME = 'Berlin'
ORGANIZATION_NAME = 'Heidelberger Druckmaschinen AG'
COMMON_NAME = 'Referenz-Client'
CERTIFICATE_VALIDITY_IN_DAYS = 720

"""The Credentials Manager provides keys, creates the csr and handles the io communication with the local file 
directory"""


class CredentialsManager:
    def __init__(self, device_cert_path: str,
                 amazon_root_ca_path: str, certificate_store_path: str,
                 device_private_key_path: str, connection_properties_path: str):

        self.device_cert_path = device_cert_path
        self.amazon_root_ca_path = amazon_root_ca_path
        self.certificate_store_path = certificate_store_path
        self.device_private_key_path = device_private_key_path
        self.connection_properties_path = connection_properties_path
        self.device_pri_key = None
        self.device_pub_key = None
        self.csr = None

    def check_needed_files(self):
        """Check if the needed files for mqtt connection are present"""
        files_to_check = [self.device_private_key_path, self.device_cert_path, self.connection_properties_path]

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

    def add_file_to_certificate_store(self, file, data):
        """Writes string to file"""
        try:
            if not os.path.exists(self.certificate_store_path):
                os.makedirs(self.certificate_store_path)
            file_handler = open(file, 'w')
            file_handler.write(data)
            file_handler.close()
        except Exception:
            message = f'file: {file} with data: {data} cannot be stored on disk'
            raise Exception(message)

    def create_csr(self) -> Dict:
        """Creates a csr and signing it with device private key"""
        self._create_keys()

        csr_issuer = x509.Name([x509.NameAttribute(NameOID.COUNTRY_NAME, COUNTRY_NAME),
                                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, STATE),
                                x509.NameAttribute(NameOID.LOCALITY_NAME, LOCALITY_NAME),
                                x509.NameAttribute(NameOID.COMMON_NAME, COMMON_NAME)])

        self.csr = x509.CertificateSigningRequestBuilder().subject_name(csr_issuer).sign(self.device_pri_key,
                                                                                         hashes.SHA256(),
                                                                                         default_backend())
        response = {}
        keys = self._serialize_key_pair()
        response.update(keys)
        response.update({'csr': self.csr.public_bytes(encoding=serialization.Encoding.PEM).decode('utf-8')})
        return response

    def _create_keys(self) -> None:
        """Creates RSA private and public key"""
        self.device_pri_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        self.device_pub_key = self.device_pri_key.public_key()

    def _serialize_key_pair(self) -> Dict:
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

        return {'private_key': device_pri_key_pem.decode('utf-8'), 'public_key': device_pub_key_pem.decode('utf-8')}
