import board
import digitalio
from pwmio import PWMOut
from adafruit_motor import motor
from analogio import AnalogIn

POT = AnalogIn(board.GP28)

button_A = digitalio.DigitalInOut(board.GP0)
button_A.direction = digitalio.Direction.INPUT
button_A.pull = digitalio.Pull.UP

button_B = digitalio.DigitalInOut(board.GP1)
button_B.direction = digitalio.Direction.INPUT
button_B.pull = digitalio.Pull.UP

PWM_M2A = PWMOut(board.GP12, frequency=10000)
PWM_M2B = PWMOut(board.GP13, frequency=10000)
dc_motor = motor.DCMotor(PWM_M2A, PWM_M2B)

motor_direction = "STOPPED"
motor_speed_percent = 0
throttle_value = 0.0

while True:
    pot_raw_value = POT.value
    speed_factor = pot_raw_value / 65535
    motor_speed_percent = speed_factor * 100

    button_A_pressed = not button_A.value
    button_B_pressed = not button_B.value

    if button_A_pressed and not button_B_pressed:
        motor_direction = "FORWARD"
        throttle_value = speed_factor
        dc_motor.throttle = throttle_value
    elif button_B_pressed and not button_A_pressed:
        motor_direction = "REVERSE"
        throttle_value = -speed_factor
        dc_motor.throttle = throttle_value
    else:
        motor_direction = "STOPPED"
        throttle_value = 0.0
        dc_motor.throttle = 0.0

    print(f"Direction: {motor_direction:15} | Speed: {motor_speed_percent:5.1f}% | Throttle: {throttle_value:6.2f}")
