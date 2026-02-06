import time
import board
import digitalio
from analogio import AnalogIn
from pwmio import PWMOut
from adafruit_motor import servo

servo1 = servo.ContinuousServo(PWMOut(board.GP6, frequency=50), min_pulse=500, max_pulse=2500)
servo2 = servo.ContinuousServo(PWMOut(board.GP7, frequency=50), min_pulse=500, max_pulse=2500)

button_A = digitalio.DigitalInOut(board.GP0)
button_B = digitalio.DigitalInOut(board.GP1)
for button in (button_A, button_B):
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP

pot = AnalogIn(board.GP28)

print("Continuous Servo Control")
print("A: Forward | B: Backward | A+B: Emergency Stop | No button: Stop")
print("=" * 50)

while True:
    pot_value = pot.value
    speed = min(1.0, pot_value / 65535)
    speed_percent = speed * 100

    a_pressed = not button_A.value
    b_pressed = not button_B.value

    if a_pressed:
        direction = "FORWARD"
        throttle = speed
    elif b_pressed:
        direction = "BACKWARD"
        throttle = -speed
    else:
        direction = "STOP"
        throttle = 0.0

    servo1.throttle = throttle
    servo2.throttle = throttle

    print(f"{direction:15} | Speed: {speed_percent:5.1f}% | Throttle: {throttle:+.2f}")
    print("-" * 50)

    time.sleep(0.1)
