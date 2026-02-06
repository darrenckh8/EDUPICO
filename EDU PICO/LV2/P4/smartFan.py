import board
import time
import busio
import adafruit_ssd1306
import neopixel
import digitalio
from pwmio import PWMOut
from adafruit_motor import motor
from analogio import AnalogIn

POT = AnalogIn(board.GP28)
i2c = busio.I2C(board.GP5, board.GP4)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

PWM_M2A = PWMOut(board.GP12, frequency=10000)
PWM_M2B = PWMOut(board.GP13, frequency=10000)
fan_motor = motor.DCMotor(PWM_M2A, PWM_M2B)

pixels = neopixel.NeoPixel(board.GP14, 5, brightness=0.2)

power_button = digitalio.DigitalInOut(board.GP0)
power_button.direction = digitalio.Direction.INPUT
power_button.pull = digitalio.Pull.UP

mode_button = digitalio.DigitalInOut(board.GP1)
mode_button.direction = digitalio.Direction.INPUT
mode_button.pull = digitalio.Pull.UP

fan_on = False
pot_mode = True
preset_speed = 0
preset_speeds = [0.3, 0.6, 1.0]
preset_names = ["LOW", "MED", "HIGH"]

def check_button(button):
    if not button.value:
        time.sleep(0.05)
        while not button.value:
            time.sleep(0.01)
        return True
    return False

def update_leds(speed):
    if not fan_on:
        pixels.fill((0, 0, 0))
        return
    if speed < 0.3:
        pixels.fill((0, 50, 0))
    elif speed < 0.7:
        pixels.fill((50, 50, 0))
    else:
        pixels.fill((50, 0, 0))

def update_display():
    oled.fill(0)
    oled.text("SMART FAN", 30, 0, 1)
    status = "ON" if fan_on else "OFF"
    oled.text(f"Power: {status}", 0, 15, 1)
    if fan_on:
        mode_text = "POT" if pot_mode else "PRESET"
        oled.text(f"Mode: {mode_text}", 0, 30, 1)
        if pot_mode:
            speed = (POT.value / 65535)
            speed_percent = int(speed * 100)
            oled.text(f"Speed: {speed_percent}%", 0, 45, 1)
        else:
            oled.text(f"Speed: {preset_names[preset_speed]}", 0, 45, 1)
    else:
        oled.text("Press PWR to start", 0, 45, 1)
    oled.show()

print("Smart Fan Controller")
print("GP0 = Power Button")
print("GP1 = Mode Button")

while True:
    if check_button(power_button):
        fan_on = not fan_on
        if not fan_on:
            fan_motor.throttle = 0
        print(f"Fan {'ON' if fan_on else 'OFF'}")
        time.sleep(0.3)
    if fan_on and check_button(mode_button):
        if pot_mode:
            pot_mode = False
            print("Switched to PRESET mode")
        else:
            preset_speed = (preset_speed + 1) % 3
            print(f"Preset speed: {preset_names[preset_speed]}")
            if preset_speed == 0:
                pot_mode = True
                print("Switched to POT mode")
        time.sleep(0.3)
    if fan_on:
        if pot_mode:
            speed = POT.value / 65535
        else:
            speed = preset_speeds[preset_speed]
        fan_motor.throttle = speed
        update_leds(speed)
    else:
        fan_motor.throttle = 0
        pixels.fill((0, 0, 0))
    update_display()
    time.sleep(0.1)
