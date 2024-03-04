from __future__ import annotations
from datetime import datetime, timedelta
import logging


class EnergyMeter:
    def __init__(self, ticks_per_kwh : int, power_time_window : timedelta, min_power_ticks : int):
        """
        ticks_per_kwh: Number of ticks per kWh
        power_time_window: Time window to calculate instantaneous power over
        min_power_ticks: Minimum ticks required in power_time_window to calculate power
        """
        self.ticks_per_kwh = ticks_per_kwh
        self.ticks : list[datetime] = []
        self.last_reset : datetime | None = None
        self.condensed_ticks : int = 0
        self.condensed_start : datetime | None = None
        self.condensed_end : datetime | None = None
        self.power_time_window = power_time_window
        self.min_power_ticks = min_power_ticks

        self.logger = logging.getLogger(__class__.__name__)

    def tick(self) -> None:
        """
        Tick the meter.
        """
        now = datetime.now()
        self.ticks.append(now)
        self.logger.debug(f"tick({now})")
    
    def stop(self) -> None:
        """
        Stop the tick provider.
        """
        raise NotImplementedError()
    
    def calculate_energy(self, since : datetime | None) -> tuple[float, float | None, datetime | None]:
        """
        Returns the energy usage since *since*, in kWh, instantaneous (last few ticks) power, and the time of the last tick.
        Resets the counter.
        """
        self.logger.debug(f"total ticks: {len(self.ticks)}")

        # Calculate energy usage.
        if since is None:
            energy_ticks = self.ticks
        else:
            energy_ticks = [tick for tick in self.ticks if tick > since]
        
        if len(energy_ticks) == 0:
            return 0, 0, None

        last_tick = energy_ticks[-1]
        n_energy_ticks = len(energy_ticks)
        if self.condensed_ticks > 0:
            if since is None:
                n_energy_ticks += self.condensed_ticks
            elif self.condensed_start is not None and self.condensed_end is not None and since < self.condensed_end:
                condensed_ticks_in_range = self._condensed_ticks_in_range(since, self.condensed_end)
                n_energy_ticks += condensed_ticks_in_range
        self.logger.debug(f"ticks since {since}: {n_energy_ticks}")
        self.logger.debug(f"last tick: {last_tick}")
        energy = len(energy_ticks) / self.ticks_per_kwh
        self.logger.debug(f"energy: {energy}")

        # Calculate instantaneous power.
        power_ticks = [tick for tick in self.ticks if tick > last_tick - self.power_time_window]
        if len(power_ticks) < self.min_power_ticks:
            instantaneous_power = None
        else:
            n_power_ticks = len(power_ticks) - 1
            energy_power_ticks = n_power_ticks / self.ticks_per_kwh
            t_power = (power_ticks[-1] - power_ticks[0]).total_seconds()
            if t_power == 0:
                instantaneous_power = None
            else:
                instantaneous_power = energy_power_ticks / t_power * 3600
            self.logger.debug(f"power: {instantaneous_power} ({n_power_ticks} ticks over {t_power} s)")

        return energy, instantaneous_power, last_tick
    
    def clear(self, before : datetime) -> None:
        """
        Clears all ticks before *before*.
        """
        ticks_to_clear = [tick for tick in self.ticks if tick < before]
        for tick in ticks_to_clear:
            self.ticks.remove(tick)
        
        # Reduced condensed ticks.
        if self.condensed_ticks > 0 and self.condensed_start is not None and self.condensed_start < before:
            condensed_ticks_in_range = self._condensed_ticks_in_range(self.condensed_start, before)
            self.condensed_ticks -= condensed_ticks_in_range
            self.condensed_start = before
        
        self.last_reset = before

    
    def condense(self, until : datetime) -> None:
        """
        Condenses all ticks until *until*.
        """
        ticks_to_condense = [tick for tick in self.ticks if tick <= until]
        self.condensed_ticks += len(ticks_to_condense)
        if self.condensed_start is None:
            self.condensed_start = ticks_to_condense[0]
        self.condensed_end = ticks_to_condense[-1]
        for tick in ticks_to_condense:
            self.ticks.remove(tick)
    
    def _condensed_ticks_in_range(self, start : datetime, end : datetime) -> int:
        """
        Returns the number of ticks in the condensed part of the interval [start, end].
        """
        if self.condensed_ticks == 0:
            return 0
        if self.condensed_start is None or self.condensed_end is None:
            return 0
        if end < self.condensed_start:
            return 0
        if start > self.condensed_end:
            return 0
        if start < self.condensed_end and self.condensed_start < end:
            return self.condensed_ticks
        if self.condensed_end < end:
            condensed_part = (self.condensed_end - start).total_seconds() / (self.condensed_end - self.condensed_start).total_seconds()
        elif start < self.condensed_start:
            condensed_part = (end - self.condensed_start).total_seconds() / (self.condensed_end - self.condensed_start).total_seconds()
        else:
            raise Exception("This should not happen.")
        return int(condensed_part * self.condensed_ticks)