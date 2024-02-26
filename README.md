# smartmeter

smartmeter monitors energy ticks on a raspberry pi GPIO pin and sends energy since last message and instantaneous power to home assistant via MQTT.

The following can be configured in local_config.py (see config.py for values to override):
- sending frequency
- window used for instantaneous power
- MQTT details
- smartmeter identifier
- GPIO pin