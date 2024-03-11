smartmeter_id = "smartmeter"
device_name = "Energy Meter"
ticks_per_kwh = 1000 # Number of ticks per kWh

gpio_pin = 14 # GPIO pin connected to energy meter
gpio_pud = "down" # Pull-up/pull-down configuration for GPIO pin (up/down)
gpio_edge = "falling" # Edge to detect for power tick (rising/falling)

mqtt_server = "127.0.0.1"
mqtt_port = 1883
mqtt_homeassistant_discovery_prefix = "homeassistant"
mqtt_user = ""
mqtt_password = ""

send_interval = 300 # Time in seconds between sending updates
instantaneous_power_time_window_in_seconds = 30 # Time window to calculate instantaneous power

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