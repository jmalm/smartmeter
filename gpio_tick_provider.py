from typing import Callable
import RPi.GPIO as GPIO


class GpioTickProvider:
    def __init__(self, tick : Callable[...,None], pin : int, pud : str, edge : str):
        """
        pin: GPIO pin to monitor
        pud: Pull-up/pull-down configuration for GPIO pin ("up"/"down")
        edge: Edge to detect for power tick ("rising"/"falling")
        """
        self.energy_meter_tick = tick
        self.gpio_pin = pin

        if pud.lower() == "down":
            pud_mode = GPIO.PUD_DOWN
        elif pud.lower() == "up":
            pud_mode = GPIO.PUD_UP
        else:
            pud_mode = None

        if edge.lower() == "rising":
            edge_mode = GPIO.RISING
        elif edge.lower() == "falling":
            edge_mode = GPIO.FALLING
        else:
            raise ValueError(f"Invalid edge to detect: {edge}")

        GPIO.setmode(GPIO.BCM)  # set up BCM GPIO numbering
        GPIO.setup(pin, GPIO.IN, pud_mode)
        GPIO.add_event_detect(pin, edge_mode, callback=self.tick_callback, bouncetime=18)    

    def tick_callback(self, _):
        self.energy_meter_tick()
    
    def stop(self):
        import RPi.GPIO as GPIO
        GPIO.cleanup()