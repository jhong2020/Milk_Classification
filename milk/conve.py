
from gpiozero import PWMOutputDevice

class ConvControl:
    def __init__(self):
        # 핀 번호 설정
        A_IA_PIN = 2
        A_IB_PIN = 3

        # PWMOutputDevice를 사용하여 PWM 핀 설정
        self.pwm_A_IA = PWMOutputDevice(A_IA_PIN)
        self.pwm_A_IB = PWMOutputDevice(A_IB_PIN)

    # 전진 (속도 조절 가능)
    def forward(self, speed):
        self.pwm_A_IA.value = speed / 100.0  # speed는 0-100 사이의 값 (0.0-1.0 사이로 변환)
        self.pwm_A_IB.value = 0.0            # A_IB는 0 (전진 방향)

    # 후진 (속도 조절 가능)
    def backward(self, speed):
        self.pwm_A_IA.value = 0.0            # A_IA는 0 (후진 방향)
        self.pwm_A_IB.value = speed / 100.0  # speed는 0-100 사이의 값 (0.0-1.0 사이로 변환)

    # 정지
    def stop(self):
        self.pwm_A_IA.value = 0.0
        self.pwm_A_IB.value = 0.0


