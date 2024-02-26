from typing import Callable
import RPi.GPIO as GPIO


class GpioTickProvider:
    def __init__(self, tick : Callable[...,None], gpio_pin : int):
        """
        gpio_pin: GPIO pin to monitor
        """
        self.energy_meter_tick = tick
        self.gpio_pin = gpio_pin

        GPIO.setmode(GPIO.BCM)  # set up BCM GPIO numbering
        GPIO.setup(gpio_pin, GPIO.IN, GPIO.PUD_DOWN)
        GPIO.add_event_detect(gpio_pin, GPIO.RISING, callback=self.tick_callback, bouncetime=18)    

    def tick_callback(self, _):
        self.energy_meter_tick()
    
    def stop(self):
        import RPi.GPIO as GPIO
        GPIO.cleanup()