import json
import os
from dataclasses import dataclass

import uuid

from onboarding.credentials_manager import CredentialsManager
from onboarding.provisioning_manager import ProvisioningManager
from onboarding.zaikio_manager import ZaikioManager


@dataclass
class ConnectionDetails:
    device_private_key_path: str
    device_cert_path: str
    amazon_root_ca_path: str
    client_id: str
    org_id: str
    site_id: str
    telemetry_topic: str
    mqtt_endpoint: str
    standard_port: int
    machine_id: str


class OnboardingManager:
    def __init__(self):
        base_path = f'{os.getcwd()}'
        self.certificate_store_path = f'{base_path}/certificate_store'
        self.amazon_root_ca_path = f'{self.certificate_store_path}/amazonRootCA1.pem'
        self.device_private_key_path = f'{self.certificate_store_path}/devicePrivateKey.pem'
        self.device_cert_path = f'{self.certificate_store_path}/deviceCert.cert'
        self.connection_properties_path = f'{self.certificate_store_path}/properties.json'

    def onboard(self) -> ConnectionDetails:
        cm = CredentialsManager(self.device_cert_path,
                                self.amazon_root_ca_path, self.certificate_store_path,
                                self.device_private_key_path, self.connection_properties_path)

        if not cm.check_needed_files():
            base_url = os.environ['base_url']
            auth_client = os.environ['DIRECTORY_OAUTH_CLIENT_ID']
            directory_host = os.environ['DIRECTORY_HOST']
            scope = os.environ['SCOPE']

            zm = ZaikioManager(auth_client, directory_host, scope)
            token = zm.run_device_auth_flow()
            onboarding_details = zm.onboard_machine(token, 'ReferenceMachine', 'ReferenceManufacturer',
                                                    str(uuid.uuid1()), 'digital_press')
            csr_properties = cm.create_csr()
            cm.add_file_to_certificate_store(self.device_private_key_path, csr_properties['private_key'])

            pm = ProvisioningManager(base_url, token, csr_properties['csr'])
            provisioning_properties = pm.provision_new_device()
            cm.add_file_to_certificate_store(self.device_cert_path, provisioning_properties['device_cert'])
            cm.add_file_to_certificate_store(self.amazon_root_ca_path, provisioning_properties['server_root_ca'])

            connection_properties = {
                'mqtt_endpoint': provisioning_properties['mqtt_endpoint'],
                'mqtt_port': int(provisioning_properties['mqtt_port']),
                'machine_region': provisioning_properties['machine_region'],
                'telemetry_topic': provisioning_properties['telemetry_topic'],
                'client_id': provisioning_properties['client_id'],
                'org_id': provisioning_properties['org_id'],
                'machine_id': onboarding_details['machine_id'],
                'site_id': onboarding_details['site_id']
            }
            cm.add_file_to_certificate_store(self.connection_properties_path, json.dumps(connection_properties,
                                                                                         indent=2))

        # loads the persisted connections information
        connection_properties = json.loads(CredentialsManager.get_file_as_string(self.connection_properties_path))

        return ConnectionDetails(self.device_private_key_path, self.device_cert_path, self.amazon_root_ca_path,
                                 connection_properties['client_id'], connection_properties['org_id'],
                                 connection_properties['site_id'], connection_properties['telemetry_topic'],
                                 connection_properties['mqtt_endpoint'], connection_properties['mqtt_port'],
                                 connection_properties['machine_id']
                                 )
