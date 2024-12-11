# led_controller.py
from gpiozero import LED


class LEDController:
    def __init__(self):
        # LED 초기화
        self.red_led = LED(21)
        self.green_led = LED(20)
        self.yellow_led = LED(16)

    def set_green(self, state):
        if state:
            self.green_led.on()
        else:
            self.green_led.off()

    def set_yellow(self, state):
        if state:
            self.yellow_led.on()
        else:
            self.yellow_led.off()

    def set_red(self, state):
        if state:
            self.red_led.on()
        else:
            self.red_led.off()

    # 컨베이어 state 추가
    def update_led_state(self, state_text):
        """상태에 따라 LED를 업데이트합니다."""
        if state_text == "Stop":
            self.set_red(True)
            self.set_green(False)
            self.set_yellow(False)
        elif state_text == "Centered":
            self.set_red(False)
            self.set_green(False)
            self.set_yellow(True)
        elif state_text == "In ROI":
            self.set_red(False)
            self.set_green(False)
            self.set_yellow(True)
        else:  # Outside ROI
            self.set_red(False)
            self.set_green(True)
            self.set_yellow(False)
