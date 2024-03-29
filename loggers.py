from datetime import datetime
import json
import logging


class Logger:
    def instantaneous_power(self, power : float) -> None:
        """Send instantaneous power"""
        raise NotImplementedError()
    
    def accumulated_energy(self, energy : float, last_reset : datetime) -> None:
        """Send accumulated energy usage"""
        raise NotImplementedError()


class LoggingLogger(Logger):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__class__.__name__)

    def instantaneous_power(self, power : float):
        self.logger.info(f"Instantaneous power: {power:.3f} kW")

    def accumulated_energy(self, energy: float, last_reset : datetime):
        self.logger.info(f"Accumulated energy since {last_reset.isoformat()}: {energy:.3f} kWh")


class MqttLogger(Logger):
    state_topic_template = "{entity_id}/{measurement}"
    config_topic_template = "{discovery_prefix}/sensor/{object_id}/config"
    power_name = "instantaneous_power"
    energy_name = "accumulated_energy"

    def __init__(self, server: str, port: int, entity_id: str, user: str, password: str, discovery_prefix: str, device_name: str):
        super().__init__()
        
        self.logger = logging.getLogger(__class__.__name__)
        self.server = server
        self.port = port
        self.entity_id = entity_id
        self.auth = {'username': user, 'password': password} if user else None
        self.discovery_prefix = discovery_prefix
        self.device_name = device_name

        self.publish_discovery()
    
    def publish_discovery(self):
        from paho.mqtt import publish
        
        # Device
        device = {
            "identifiers": [self.entity_id],
            "name": self.device_name
        }

        # Instantaneous power
        power_object_id = f"{self.entity_id}_{self.power_name}"
        power_config_topic = self.config_topic_template.format(discovery_prefix=self.discovery_prefix,
                                                               object_id=power_object_id)
        power_state_topic = self.state_topic_template.format(entity_id=self.entity_id,
                                                             measurement=self.power_name)
        power_config = {
            "name": "Instantaneous power",
            "unit_of_measurement": "kW",
            "state_topic": power_state_topic,
            "device_class": "power",
            "value_template": "{{ value_json.power }}",
            "unique_id": power_object_id,
            "device": device
        }

        # Energy
        energy_object_id = f"{self.entity_id}_{self.energy_name}"
        energy_config_topic = self.config_topic_template.format(discovery_prefix=self.discovery_prefix,
                                                                object_id=energy_object_id)
        energy_state_topic = self.state_topic_template.format(entity_id=self.entity_id,
                                                              measurement=self.energy_name)
        energy_config = {
            "name": "Energy",
            "unit_of_measurement": "kWh",
            "state_topic": energy_state_topic,
            "device_class": "energy",
            "value_template": "{{ value_json.energy }}",
            "state_class": "total",
            "unique_id": energy_object_id,
            "device": device
        }

        # Publish discovery
        messages = [{"topic": power_config_topic, "payload": json.dumps(power_config), 'retain': True, 'qos': 1},
                    {"topic": energy_config_topic, "payload": json.dumps(energy_config), 'retain': True, 'qos': 1}]
        publish.multiple(messages, hostname=self.server, port=self.port, auth=self.auth) # type: ignore
        self.logger.info(f"Published discovery for {self.entity_id}")
        self.logger.debug(f"Discovery messages: {messages}")
    
    def instantaneous_power(self, power: float):
        from paho.mqtt import publish
        topic = self.state_topic_template.format(entity_id=self.entity_id, measurement=self.power_name)
        message = {"power": power, "unit_of_measurement": "kW"}
        publish.single(topic, payload=json.dumps(message), hostname=self.server, port=self.port, auth=self.auth) # type: ignore

    def accumulated_energy(self, energy: float, last_reset: datetime):
        from paho.mqtt import publish
        topic = self.state_topic_template.format(entity_id=self.entity_id, measurement=self.energy_name)
        message = {"energy": energy, "unit_of_measurement": "kWh", "last_reset": last_reset.isoformat()}
        publish.single(topic, payload=json.dumps(message), hostname=self.server, port=self.port, auth=self.auth) # type: ignore