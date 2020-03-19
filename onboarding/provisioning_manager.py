import json
import logging

import requests
from typing import Dict

logger = logging.getLogger(__name__)

"""The ProvisioningManager implements the communication with the Provisioning services"""


class ProvisioningManager:
    def __init__(self, base_url: str, token: str, csr: str):
        self.base_url = base_url
        self.auth_token = token
        self.csr = csr

    def provision_new_device(self) -> Dict:
        """Provisions a new device/client in provisioning service"""
        resp = {}
        config = self._fetch_configuration()
        resp.update(config)
        provisioning = self._fetch_provisioning()
        resp.update(provisioning)
        return resp

    def _provide_header(self):
        return {'Accept': 'application/json', 'Authorization': f'Bearer {self.auth_token}'}

    def _fetch_configuration(self) -> Dict:
        """call the configuration API"""
        config_url = f'{self.base_url}/v3/configuration'
        response = requests.get(config_url, headers=self._provide_header())
        if response.status_code == 200:
            content = response.json()
            logger.debug(content)
            certificate_data = content['connectivity']['serverRootCA']
            mqtt_endpoint = content['connectivity']['mqttEndPoint']
            mqtt_port = content['connectivity']['mqttPort']
            machine_region = content['connectivity']['machineRegion']
            telemetry_topic = content['provisioning']['telemetryTopic']
            return {
                "mqtt_endpoint": mqtt_endpoint,
                "mqtt_port": mqtt_port,
                "machine_region": machine_region,
                "telemetry_topic": telemetry_topic,
                "server_root_ca": certificate_data
            }
        raise Exception('configuration api call not successful')

    def _fetch_provisioning(self) -> Dict:
        """call the provisioning API"""
        logger.info('Starting provisioning...')
        provisioning_url = f'{self.base_url}/v3/provisioning'
        response = requests.post(provisioning_url, headers=self._provide_header(), data=self._build_provisioning_body())
        if response.status_code == 200:
            content = response.json()
            device_cert_data = content['deviceCert']
            client_id_data = content['clientId']
            org_id_data = content['orgId']

            return {
                "device_cert": device_cert_data,
                "client_id": client_id_data,
                "org_id": org_id_data
            }

        raise Exception('Provisioning API call not successful')

    def _build_provisioning_body(self):
        """Provide body payload for provisioning request"""
        return json.dumps({"certificateSigningRequest": self.csr})
