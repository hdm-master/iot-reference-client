import logging
import ssl
from dataclasses import dataclass
import paho.mqtt.client as paho

logger = logging.getLogger(__name__)


@dataclass
class SenderDetails:
    mqtt_endpoint: str
    standard_port: int
    device_cert_path: str
    device_private_key_path: str
    amazon_root_ca_path: str
    sendertype: str
    sendername: str
    sendersoftwareversion: str
    telemetry_topic: str
    org_id: str
    site_id: str
    thing_name: str


class Sender:
    """ Sender
    This class handles the connectivity to the iot core. The sender
    uses this class to connect to the IoT Core, receive updates and publish
    state changes and telemetry messages
    """
    iot_protocol_name = "x-amzn-mqtt-ca"

    def __init__(self, options: SenderDetails):
        self.endpoint = options.mqtt_endpoint
        self.standard_port = options.standard_port
        self.client_id = options.thing_name
        self.cert_path = options.device_cert_path
        self.key_path = options.device_private_key_path
        self.ca_server_path = options.amazon_root_ca_path
        self.telemetry_topic = options.telemetry_topic
        self.org_id = options.org_id
        self.site_id = options.site_id
        self.thing_name = options.thing_name
        self.sendertype = options.sendertype
        self.sendername = options.sendername
        self.sendersoftwareversion = options.sendersoftwareversion
        self.mqttc = paho.Client(client_id=self.client_id)

    def connect(self, ssl_tunnel=False):
        """Setup the mqtt connection to use standard port"""
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.on_disconnect = self.on_disconnect
        if ssl_tunnel:
            port = 443
            self.mqttc.tls_set_context(context=self.ssl_alpn())
        else:
            port = self.standard_port
            self.mqttc.tls_set(ca_certs=self.ca_server_path, certfile=self.cert_path, keyfile=self.key_path)
        self.mqttc.connect(self.endpoint, port, keepalive=120)
        logger.info('Connection to endpoint: %s' % self.endpoint)
        logger.info('Connection via port: %s' % port)
        self.mqttc.loop_start()  # starts a new thread to handle mqtt IO

    def ssl_alpn(self):
        """Create the ssl context for the tls connection"""
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.set_alpn_protocols([Sender.iot_protocol_name])
            ssl_context.load_verify_locations(cafile=self.ca_server_path)
            ssl_context.load_cert_chain(
                certfile=self.cert_path,
                keyfile=self.key_path)
            return ssl_context
        except Exception as exception:
            logger.error("Error using ssl tunnel")
            raise exception

    def publish_telemetry(self, message: str):
        """publish message to dedicated telemetry topic"""
        self.publish(f'{self.telemetry_topic}/{self.org_id}/{self.client_id}', message)

    def disconnect(self):
        """Disconnects the mqtt iot_assets"""
        self.mqttc.disconnect()

    def publish(self, topic, message):
        """publishes a message via the mqtt iot_assets"""
        logger.info('Publishing to topic: %s' % topic)
        logger.info('Message: %s' % message)
        self.mqttc.publish(topic, message, qos=1)

    def subscribe(self, topic):
        """subscribes to a mqtt topic"""
        logger.info(f'Subscribing to topic: {topic}')
        self.mqttc.subscribe(topic, qos=1)

    def on_connect(self, client, flags, result_code):
        """On connect callback handler"""
        logger.info('Connected client: %s' % client)
        logger.info('Result is: %i' % result_code)

    def on_message(self, client, userdata, msg):
        """On message callback handler"""

    def on_disconnect(self, client, result_code):
        """disconnect callback handler"""
        logger.info('Disconnecting client: %s' % client)
        logger.info('Result is: %i' % result_code)
