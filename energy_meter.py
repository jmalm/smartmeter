from __future__ import annotations
from datetime import datetime, timedelta
import logging


class EnergyMeter:
    def __init__(self, ticks_per_kwh : int, power_time_window : timedelta):
        """
        ticks_per_kwh: Number of ticks per kWh
        power_time_window: Time window to calculate instantaneous power over
        """
        self.ticks : list[datetime] = []
        self.power_time_window = power_time_window

        self.logger = logging.getLogger(__class__.__name__)

        self.energy_per_tick_kwh = 1 / ticks_per_kwh
        self.accumulated_energy_kwh = 0

        self.started = datetime.now()

    def tick(self) -> None:
        """
        Tick the meter.
        """
        now = datetime.now()
        self.ticks.append(now)
        self.logger.debug(f"tick({now})")

        self.accumulated_energy_kwh += self.energy_per_tick_kwh

    @property
    def instantaneous_power_kw(self) -> float:
        # Filter ticks to only those within the power time window
        ticks_in_window = [t for t in self.ticks if t > datetime.now() - self.power_time_window]
        
        energy_kwh = len(ticks_in_window) * self.energy_per_tick_kwh
        t_delta_h = self.power_time_window.total_seconds() / 3600

        return energy_kwh / t_delta_h