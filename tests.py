from datetime import datetime, timedelta
import unittest

from energy_meter import EnergyMeter


class TestEnergyMeter(unittest.TestCase):
    def test_accumulated_energy(self):
        """Test accumulated energy calculation"""
        # Arrange
        meter = EnergyMeter(1000, timedelta(seconds=10))

        # Act
        meter.tick()
        meter.tick()
        meter.tick()

        # Assert
        self.assertEqual(meter.accumulated_energy_kwh, 3 / 1000)
    
    def test_instantaneous_power(self):
        """Test instantaneous power calculation"""
        # Arrange
        power_time_window = timedelta(seconds=10)
        meter = EnergyMeter(1000, power_time_window)

        # Act
        meter.tick()
        meter.tick()
        meter.tick()

        # Assert
        t_delta_h = power_time_window.total_seconds() / 3600
        expected_power_kw = (3 / 1000) / t_delta_h
        self.assertAlmostEqual(meter.instantaneous_power_kw, expected_power_kw)
    
    def test_instantaneous_power_no_ticks(self):
        """Test instantaneous power calculation with no ticks during time window"""
        # Arrange
        power_time_window = timedelta(seconds=10)
        meter = EnergyMeter(1000, power_time_window)

        # Act

        # Assert
        self.assertAlmostEqual(meter.instantaneous_power_kw, 0)
    
    def test_instantaneous_power_old_ticks(self):
        """Test instantaneous power calculation with ticks outside time window"""
        # Arrange
        power_time_window = timedelta(seconds=10)
        meter = EnergyMeter(1000, power_time_window)

        # Act
        meter.ticks = [
            datetime(2022, 1, 1, 0, 0, 1),
            datetime(2022, 1, 1, 0, 0, 3),
            datetime(2022, 1, 1, 0, 0, 4)
        ]
        meter.tick()

        # Assert
        t_delta_h = power_time_window.total_seconds() / 3600
        expected_power_kw = (1 / 1000) / t_delta_h
        self.assertAlmostEqual(meter.instantaneous_power_kw, expected_power_kw)


if __name__ == '__main__':
    unittest.main()