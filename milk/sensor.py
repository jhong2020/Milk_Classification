# sensor.py
from gpiozero import DigitalInputDevice

class InfraredSensor:
    def __init__(self, pin=15):
        # S601 적외선 센서 초기화 (GPIO 핀 번호 지정)
        self.sensor = DigitalInputDevice(pin)

    def is_object_detected(self):    
        return self.sensor.value == 0 
    

class InfraredSensor2:
    def __init__(self, pin2=14):
        self.sensor2 = DigitalInputDevice(pin2)

    def is_object_limits(self):
        return self.sensor2.value == 0