import logging
import random
import threading
import time
from typing import Callable


def create_step(period_s : int, low_kw : float, high_kw : float) -> Callable[..., float]:
    start = time.time()

    def power():
        """Returns *low* or *high* on periodic basis."""
        seconds_since_start = time.time() - start
        part_of_period = (seconds_since_start % period_s) / period_s
        logging.getLogger("create_step.power").debug(f"Remainder: {part_of_period}")
        if part_of_period > 0.5:
            return high_kw
        else:
            return low_kw
    
    return power


def create_slowly_varying_random(low_kw : float, high_kw : float) -> Callable[..., float]:
    class SlowlyVaryingRandom:
        last_power = random.uniform(low_kw, high_kw)
        
        def __call__(self) -> float:
            # Modify power usage by 10 % each time it is requested.
            self.last_power = self.last_power * (1 + random.uniform(-0.1, 0.1))
            if self.last_power > high_kw:
                # We're at the highest power, just pick a random value.
                self.last_power = random.uniform(low_kw, high_kw)
            if self.last_power < low_kw:
                # We're at the lowest power, just pick a random value.
                self.last_power = random.uniform(low_kw, high_kw)
            return self.last_power

    return SlowlyVaryingRandom()


class EmulatorTickProvider:
    longest_sleep_s = 1

    def __init__(self, tick : Callable[..., None], power : Callable[..., float], ticks_per_kwh : int, power_range : tuple[float, float]):
        """
        ticks_per_kwh: Number of ticks per kWh
        power_range: (min, max) of power to emulate, in kW

        Note: Don't set min power to too low, or you may have to wait a long time for the
        next tick.
        """
        self.energy_meter_tick = tick
        self.ticks_per_kwh = ticks_per_kwh
        self.get_emulated_power_usage = power

        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.run, args=(self.stop_event,))
        self.thread.start()

        self.logger = logging.getLogger(__class__.__name__)


    def run(self, stop_event : threading.Event):
        last = time.time()
        while True:
            if stop_event.is_set():
                break
            
            power_kw = self.get_emulated_power_usage()
            self.logger.debug(f"Emulated power: {power_kw:.2f} kW")
            if power_kw == 0:
                # Just sleep a bit and get a new power usage
                time.sleep(self.longest_sleep_s)
                continue

            # Tick every 1/self.ticks_per_kwh kWh
            seconds_per_tick = (1 / self.ticks_per_kwh) / power_kw * 3600
            time_to_sleep_s = min(seconds_per_tick, self.longest_sleep_s)
            time.sleep(time_to_sleep_s)
            now = time.time()
            if now - last >= seconds_per_tick:
                self.energy_meter_tick()
                last = now
        
    def stop(self):
        self.stop_event.set()
        self.thread.join()