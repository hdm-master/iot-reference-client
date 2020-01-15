import paho.mqtt.client as paho
from util.connectionHelper import IoTConnectionException
from util.log import get_logger

logger = get_logger(__name__)


class IoTClientException(Exception):
    def __init__(self, message="IoT Client failed", status_code=500, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class IoTClient:
    """ The IoT Core Client

    This class handles the connectivity to the iot core. The device
    uses this class to connect to the IoT Core, receive updates and publish
    state changes and telemetry messages
    """

    def __init__(self, device, connection_details):
        self.device = device
        self.endpoint = connection_details['endpoint']
        self.standard_port = connection_details['standard_port']
        self.thing_name = connection_details['clientId']
        self.cert_path = connection_details['device_cert_path']
        self.key_path = connection_details['device_private_key_path']
        self.ca_server_path = connection_details['amazon_root_ca_path']
        self.mqttc = paho.Client(client_id=self.thing_name)
        self.connflag = False  # unclear use

    def connect(self):
        """Setup the mqtt connection to use standard port"""
        try:
            self.mqttc.on_connect = self.on_connect
            self.mqttc.on_message = self.on_message
            self.mqttc.on_disconnect = self.on_disconnect
            self.mqttc.tls_set(ca_certs=self.ca_server_path, certfile=self.cert_path, keyfile=self.key_path)
            self.mqttc.connect(self.endpoint, int(self.standard_port), keepalive=120)
            logger.info('Connection to endpoint: %s' % self.endpoint)
            logger.info('Connection via port: %s' % self.standard_port)
            self.mqttc.loop_start()  # starts a new thread to handle mqtt IO
        except IoTConnectionException as err:
            raise err
        except Exception as err:
            raise IoTClientException(message="iot client connection failed", details=err)

    def disconnect(self):
        """Disconnects the mqtt demo_client"""

        self.mqttc.disconnect()

    def publish(self, topic, message):
        """publishes a message via the mqtt demo_client"""

        logger.debug('Publishing to topic: %s' % topic)
        logger.debug('Message: %s' % message)
        self.mqttc.publish(topic, message, qos=1)

    def subscribe(self, topic):
        """subscribes to a mqtt topic"""
        logger.debug(f'Subscribing to topic: {topic}')
        self.mqttc.subscribe(topic, qos=1)

    def on_connect(self, client, userdata, flags, result_code):
        """On connect callback handler"""

        # self.connflag = True

    def on_message(self, client, userdata, msg):
        """On message callback handler"""

    def on_disconnect(self, client, userdata, result_code):
        """disconnect callback handler"""
        # self.connflag = False
        logger.info('Disconnecting client: %s' % self.thing_name)
        logger.info('Result is: %i' % result_code)
        client.connected_flag = False
        client.disconnect_flag = True
