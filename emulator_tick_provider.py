import logging
import random
import threading
import time
from typing import Callable


class EmulatorTickProvider:
    def __init__(self, tick : Callable[..., None], ticks_per_kwh : int, power_range : tuple[float, float]):
        """
        ticks_per_kwh: Number of ticks per kWh
        power_range: (min, max) of power to emulate, in kW

        Note: Don't set min power to too low, or you may have to wait a long time for the
        next tick.
        """
        self.energy_meter_tick = tick
        self.ticks_per_kwh = ticks_per_kwh
        self.power_range = power_range
        self.last_power = random.uniform(self.power_range[0], self.power_range[1])

        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.run, args=(self.stop_event,))
        self.thread.start()

        self.logger = logging.getLogger(__class__.__name__)


    def run(self, stop_event : threading.Event):
        while True:
            if stop_event.is_set():
                break
            
            power_kw = self.get_emulated_power_usage()
            self.logger.debug(f"Emulated power: {power_kw:.2f} kW")
            if power_kw == 0:
                # Just sleep a bit and get a new power usage
                time.sleep(1)
                continue

            # Tick every 1/self.ticks_per_kwh kWh
            seconds_per_tick = (1 / self.ticks_per_kwh) / power_kw * 3600
            time.sleep(seconds_per_tick)
            self.energy_meter_tick()
        
    def stop(self):
        self.stop_event.set()
        self.thread.join()


    def get_emulated_power_usage(self):
        """Current power, in kW"""
        # Modify power usage by 10 % each time it is requested.
        self.last_power = self.last_power * (1 + random.uniform(-0.1, 0.1))
        if self.last_power > self.power_range[1]:
            # We're at the max power, just pick a random value.
            self.last_power = random.uniform(self.power_range[0], self.power_range[1])
        if self.last_power > self.power_range[1]:
            # We're at the max power, just pick a random value.
            self.last_power = random.uniform(self.power_range[0], self.power_range[1])
        return self.last_power