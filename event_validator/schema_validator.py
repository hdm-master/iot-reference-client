import json
import os
from os.path import dirname, join

from jsonschema import validate

HEADER_FILE_NAME = "header.schema.json"
CURRENT_DIR = dirname(__file__)

PATHS = {
    "path_to_header": join(CURRENT_DIR, 'header'),
    "path_to_payload": join(CURRENT_DIR, 'payload'),
    "header_file_name": HEADER_FILE_NAME,
}


class EventValidator:
    def __init__(self, paths):
        self.path_to_header = paths['path_to_header']
        self.header_file_name = paths['header_file_name']
        self.path_to_payload = paths['path_to_payload']
        self.message = None

    @staticmethod
    def load_json(file_path):
        if os.path.isfile(file_path):
            with open(file_path) as p:
                data = json.load(p)
                return data
        else:
            raise Exception("file not found")

    @staticmethod
    def file_exists(file_path):
        return os.path.isfile(file_path)

    def validate_header(self) -> None:
        try:
            header_version = self.message ['headerversion']
            path = f'{self.path_to_header}' \
                   f'/{header_version}/{self.header_file_name}'
            schema = EventValidator.load_json(path)
            validate(instance=self.message , schema=schema)
        except Exception as err:
            raise SchemaValidationException(details=err)

    def validate_payload(self, payload_path: str) -> None:
        try:
            payload_schema = EventValidator.load_json(payload_path)
            validate(instance=self.message['payload'],
                     schema=payload_schema)
        except Exception as err:
            raise SchemaValidationException(details=err)

    def validate(self, message: str):
        try:
            self.message = self.message = json.loads(message)
            self.validate_header()
            event_type = self.message .get('eventtype')
            event_subtype = self.message .get('eventsubtype')
            event_version = self.message .get('payloadversion')
            file_name = f'{event_subtype}.schema.json'
            payload_path = join(self.path_to_payload,
                                event_type,
                                event_subtype,
                                str(event_version),
                                file_name)
            if not EventValidator.file_exists(payload_path):
                raise SchemaValidationException("Payload Schema not available")
            self.validate_payload(payload_path)
        except Exception as err:
            raise SchemaValidationException(details=err)


def event_validator_factory() -> EventValidator:
    return EventValidator(PATHS)


class SchemaValidationException(Exception):
    def __init__(self, message="Invalid schema", details=None):
        super().__init__(message)
        self.details = details or {}