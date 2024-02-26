from __future__ import annotations
"""
Monitors ticks from a smart meter on GPIO and sends the energy usage to homeassistant
over MQTT.

"""

from datetime import datetime
import time
import config
from loggers import MqttLogger, StdoutLogger
from energy_meter import EnergyMeter
import logging


def validate_config():
    if config.ticks_per_kwh <= 0:
        raise ValueError("config.ticks_per_kwh must be > 0")
    if config.send_interval <= 0:
        raise ValueError("config.send_interval must be > 0")
    if config.instantaneous_power_time_window_in_seconds <= 0:
        raise ValueError("config.instantaneous_power_time_window_in_seconds must be > 0")
    if config.instantaneous_power_time_window_in_seconds > config.send_interval:
        raise ValueError("config.instantaneous_power_time_window_in_seconds must be <= config.send_interval")


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        help="verbose output")
    parser.add_argument("-e", "--emulate", action="store_true",
                        help="emulate power blink")
    args = parser.parse_args()
    validate_config()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


    stdout_logger = StdoutLogger()
    mqtt_logger = MqttLogger(config.mqtt_server,
                             config.mqtt_port,
                             config.entity_id,
                             config.mqtt_user,
                             config.mqtt_password,
                             config.mqtt_homeassistant_discovery_prefix)
    loggers = [stdout_logger, mqtt_logger]

    energy_meter = EnergyMeter(ticks_per_kwh=config.ticks_per_kwh)
    
    # Start the tick provider up.
    emulator = None
    gpio = None
    if args.emulate:
        from emulator_tick_provider import EmulatorTickProvider
        emulator = EmulatorTickProvider(energy_meter.tick, ticks_per_kwh=config.ticks_per_kwh, power_range=(1, 5))
    else:
        from gpio_tick_provider import GpioTickProvider
        gpio = GpioTickProvider(energy_meter.tick, gpio_pin=config.gpio_pin)
    
    last_sent_energy = datetime.now()
    while True:
        try:
            time.sleep(config.send_interval)
            energy, instantaneous_power, last_tick = energy_meter.calculate_energy(last_sent_energy)
            try:
                for logger in loggers:
                    logger.energy(energy)
                    logger.instantaneous_power(instantaneous_power)
            except Exception as e:
                logging.error(f"Error logging energy: {e}")
            else:
                if last_tick:
                    energy_meter.clear(last_tick)
                    # TODO: Accumulate energy and just condense instead of clearing.
                    last_sent_energy = last_tick
        except KeyboardInterrupt:
            break
    
    if gpio:
        gpio.stop()
    if emulator:
        emulator.stop()
    

if __name__ == "__main__":
    main()