from datetime import datetime, timedelta
import unittest

from energy_meter import EnergyMeter


class TestEnergyMeter(unittest.TestCase):
    def test_calculate_energy(self):
        """Test calculate_energy method, all ticks included."""
        #########
        # Arrange
        meter = EnergyMeter(1000, timedelta(seconds=10), 2)
        start_tick = datetime(2022, 1, 1, 0, 0, 0)
        end_tick = datetime(2022, 1, 1, 0, 0, 2)
        meter.ticks = [
            start_tick,
            datetime(2022, 1, 1, 0, 0, 1),
            end_tick
        ]
        power_time_delta_h = (end_tick - start_tick).total_seconds() / 3600
        power_energy_kwh = 2 / 1000
        expected_power_kw = power_energy_kwh / power_time_delta_h

        #########
        # Act
        energy, power, last_tick = meter.calculate_energy(None)

        #########
        # Assert
        self.assertEqual(energy, 3 / 1000)
        self.assertEqual(power, expected_power_kw)
        self.assertEqual(last_tick, end_tick)
        
    def test_calculate_energy_from_datetime(self):
        """Test calculate_energy method, including ticks since datetime for energy."""
        #########
        # Arrange
        meter = EnergyMeter(1000, timedelta(seconds=10), 2)
        start_tick = datetime(2022, 1, 1, 0, 0, 0)
        end_tick = datetime(2022, 1, 1, 0, 0, 5)
        since = datetime(2022, 1, 1, 0, 0, 2)
        meter.ticks = [
            start_tick,
            datetime(2022, 1, 1, 0, 0, 1),
            datetime(2022, 1, 1, 0, 0, 3),
            datetime(2022, 1, 1, 0, 0, 4),
            end_tick
        ]
        expected_energy_kwh = 3 / 1000
        power_time_delta_h = (end_tick - start_tick).total_seconds() / 3600
        power_energy_kwh = 4 / 1000
        expected_power_kw = power_energy_kwh / power_time_delta_h

        #########
        # Act
        energy, power, last_tick = meter.calculate_energy(since)

        #########
        # Assert
        self.assertAlmostEqual(energy, expected_energy_kwh)
        self.assertIsNotNone(power)
        self.assertAlmostEqual(power, expected_power_kw) # type: ignore
        self.assertEqual(last_tick, end_tick)
        
    def test_calculate_energy_limit_power_ticks(self):
        """Test calculate_energy method, limiting power calculation ticks to window."""
        #########
        # Arrange
        meter = EnergyMeter(1000, timedelta(seconds=10), 2)
        start_tick = datetime(2022, 1, 1, 0, 0, 0)
        end_tick = datetime(2022, 1, 1, 0, 0, 20)
        since = datetime(2022, 1, 1, 0, 0, 2)
        meter.ticks = [
            start_tick,
            datetime(2022, 1, 1, 0, 0, 1),
            datetime(2022, 1, 1, 0, 0, 3),
            datetime(2022, 1, 1, 0, 0, 4),
            datetime(2022, 1, 1, 0, 0, 14),
            datetime(2022, 1, 1, 0, 0, 15),
            end_tick
        ]
        expected_energy_kwh = 5 / 1000
        power_time_delta_h = (end_tick - datetime(2022, 1, 1, 0, 0, 14)).total_seconds() / 3600
        power_energy_kwh = 2 / 1000
        expected_power_kw = power_energy_kwh / power_time_delta_h

        #########
        # Act
        energy, power, last_tick = meter.calculate_energy(since)

        #########
        # Assert
        self.assertAlmostEqual(energy, expected_energy_kwh)
        self.assertIsNotNone(power)
        self.assertAlmostEqual(power, expected_power_kw) # type: ignore
        self.assertEqual(last_tick, end_tick)
        
    def test_calculate_energy_not_enough_power_ticks(self):
        """Test calculate_energy method, not enough ticks in power time window."""
        #########
        # Arrange
        meter = EnergyMeter(1000, timedelta(seconds=10), 4)
        start_tick = datetime(2022, 1, 1, 0, 0, 0)
        end_tick = datetime(2022, 1, 1, 0, 0, 20)
        since = None
        meter.ticks = [
            start_tick,
            datetime(2022, 1, 1, 0, 0, 1),
            datetime(2022, 1, 1, 0, 0, 3),
            datetime(2022, 1, 1, 0, 0, 4),
            datetime(2022, 1, 1, 0, 0, 14),
            datetime(2022, 1, 1, 0, 0, 15),
            end_tick
        ]

        #########
        # Act
        _, power, _ = meter.calculate_energy(since)

        #########
        # Assert
        self.assertIsNone(power)
        
    def test_calculate_energy_0_power_time(self):
        """Test calculate_energy method, ticks time diff for power calculation is 0."""
        #########
        # Arrange
        meter = EnergyMeter(1000, timedelta(seconds=10), 2)
        start_tick = datetime(2022, 1, 1, 0, 0, 0)
        end_tick = datetime(2022, 1, 1, 0, 0, 20)
        since = None
        meter.ticks = [
            start_tick,
            datetime(2022, 1, 1, 0, 0, 1),
            datetime(2022, 1, 1, 0, 0, 3),
            datetime(2022, 1, 1, 0, 0, 4),
            end_tick,
            end_tick
        ]

        #########
        # Act
        _, power, _ = meter.calculate_energy(since)

        #########
        # Assert
        self.assertIsNone(power)



if __name__ == '__main__':
    unittest.main()