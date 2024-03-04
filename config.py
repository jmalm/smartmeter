smartmeter_id = "smartmeter"
gpio_pin = 14
mqtt_server = "127.0.0.1"
mqtt_port = 1883
mqtt_homeassistant_discovery_prefix = "homeassistant"
mqtt_user = ""
mqtt_password = ""
ticks_per_kwh = 1000
send_interval = 300
instantaneous_power_time_window_in_seconds = 30
minimum_number_of_power_ticks = 3

try:
    # Overwite default config values if provided in local_config.py.
    from local_config import *
except ImportError:
    import logging
    logging.getLogger(__name__).warning("No local config file found, using defaults")

# Set entity_id if it's not explicitly set in local_config.py.
try:
    entity_id
except NameError:
    entity_id = f"{smartmeter_id}_{gpio_pin}"