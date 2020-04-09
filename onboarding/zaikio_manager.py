import json
import logging
import requests
import time
from typing import Dict

logger = logging.getLogger(__name__)

"""The ZaikoManager implements the communication with the zaikio directory"""


class ZaikioManager:
    def __init__(self, auth_client: str, directory_host: str, scope: str) -> None:
        self.auth_client = auth_client
        self.directory_host = directory_host
        self.scope = scope

    def run_device_auth_flow(self) -> str:
        """start the device auth flow
        https://docs.zaikio.com/guide/oauth/device-flow.html#device-authentication-flow
        """
        logger.info('Start the device auth flow')
        token = self._authorize()
        logger.info('Here is your token:')
        logger.info(token)
        return token

    def _authorize(self) -> str:
        response = requests.post(f'{self.directory_host}/oauth/device_authorizations/authorize?client_id='
                                 f'{self.auth_client}&scope={self.scope}', headers={'Accept': 'application/json'})
        if response.status_code == 200:
            content = response.json()
            logger.info('Hello machine operator. Please go to the following website, login and choose the '
                        'organisation the IoT app should be assigned to')
            logger.info(content['verification_uri_complete'])
            logger.info(f'This is your code you have to enter: {content["user_code"]} ')
            logger.info(f'Hurry up. You have {content["expires_in"]} seconds to finish')
            return self._check_device_authorization(content['interval'], content['device_code'])
        else:
            raise Exception('Something went wrong. Authorization not possible')

    def _check_device_authorization(self, interval, device_code) -> str:
        time.sleep(interval)
        body = {
            "client_id": self.auth_client,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code
        }
        response = requests.post(f'{self.directory_host}/oauth/access_token', data=body)
        content = response.json()
        if response.status_code == 200:
            return content['access_token']
        elif response.status_code == 400:
            if content['error'] == 'expired_token':
                logger.info('What took you so long? Time is up!')
                raise Exception('User code expired. Please try again')
            elif content['error'] == 'authorization_pending':
                return self._check_device_authorization(interval, device_code)
            elif content['error'] == 'slow_down':
                logger.info('Retrying too fast. Will slow down')
                backoff = interval * 2
                return self._check_device_authorization(backoff, device_code)
        elif response.status_code == 404:
            raise Exception('Something went wrong. Authorization not possible')
        else:
            raise Exception('Technical Error')

    def onboard_machine(self, token: str, name: str, manufacturer: str,
                        serial_no: str, kind: str) -> Dict:
        """service method to add a new machine to the zaikio directory"""
        site_id = self._get_site(token)
        machine_id = self._post_machine(token, name, manufacturer, serial_no, kind)
        self._post_machine_ownership(token, machine_id, site_id)
        return {'machine_id': machine_id, 'site_id': site_id}

    def _get_site(self, token: str) -> str:
        """returns first maintained site of the organization"""
        response = requests.get(f'{self.directory_host}/api/v1/sites',
                                headers=ZaikioManager._build_header(token))

        if response.status_code == 200:
            content = response.json()
            return content[0]['id']
        else:
            raise Exception(response.reason)

    def _post_machine(self, token: str, name: str, manufacturer: str,
                      serial_no: str, kind: str) -> str:
        """creates machine in dictionary and returns machine id"""
        response = requests.post(f'{self.directory_host}/api/v1/machines?machine[name]={name}&machine[manufacturer]='
                                 f'{manufacturer}&machine[serial_number]={serial_no}&machine[kind]={kind}',
                                 headers=ZaikioManager._build_header(token))
        content = response.json()
        if response.status_code == 201:
            return content['id']
        elif response.status_code == 422:
            errors = content.get('errors')
            raise Exception(f'{errors}')
        elif 400 <= response.status_code < 500:
            raise Exception(response.reason)
        else:
            raise Exception('Technical Error')

    def _post_machine_ownership(self, token: str, machine_id: str, site_id: str) -> None:
        """adds ownership to a machine id"""
        response = requests.post(
            f'{self.directory_host}/api/v1/machines/{machine_id}/machine_ownership?site_id={site_id}',
            headers=ZaikioManager._build_header(token))

        if response.status_code != 201:
            raise Exception(response.reason)

    @staticmethod
    def _build_header(token):
        return {'Accept': 'application/json',
                'Authorization': f'Bearer {token}'}
