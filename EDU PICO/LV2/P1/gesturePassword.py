import board
import busio
import time
import neopixel
import digitalio
import adafruit_ssd1306
from adafruit_apds9960.apds9960 import APDS9960

i2c = busio.I2C(board.GP5, board.GP4)
apds = APDS9960(i2c)
apds.enable_gesture = True
apds.enable_proximity = True

oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
pixels = neopixel.NeoPixel(board.GP14, 1, brightness=0.2)

relay = digitalio.DigitalInOut(board.GP22)
relay.direction = digitalio.Direction.OUTPUT

button_A = digitalio.DigitalInOut(board.GP0)
button_B = digitalio.DigitalInOut(board.GP1)
for button in (button_A, button_B):
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP

UP, DOWN, LEFT, RIGHT = 1, 2, 3, 4
PASSWORD = [UP, LEFT, DOWN, RIGHT]

GESTURE_NAMES = {1: "UP", 2: "DOWN", 3: "LEFT", 4: "RIGHT"}
GESTURE_COLORS = {1: (0, 255, 0), 2: (255, 0, 0), 3: (0, 0, 255), 4: (255, 255, 0)}

entered_gestures = []
access_granted = False
relay_on = False
last_action_time = time.monotonic()

GESTURE_TIMEOUT = 5
SESSION_TIMEOUT = 30

def clear_pixel():
    pixels.fill((0, 0, 0))

def set_relay(state):
    global relay_on
    relay_on = state
    relay.value = state
    pixels.fill((0, 255, 0) if state else (255, 0, 0))
    time.sleep(0.3)
    clear_pixel()

def button_pressed(button):
    if not button.value:
        time.sleep(0.05)
        return not button.value
    return False

def reset_system():
    global entered_gestures, access_granted, last_action_time
    entered_gestures = []
    access_granted = False
    clear_pixel()
    last_action_time = time.monotonic()
    print("System Locked.")
    show_screen()

def show_screen():
    oled.fill(0)
    if access_granted:
        oled.text("ACCESS GRANTED", 5, 5, 1)
        oled.text(f"Relay: {'ON' if relay_on else 'OFF'}", 5, 20, 1)
        oled.text("A: Lock", 5, 40, 1)
        oled.text("B: Toggle Relay", 5, 50, 1)
    else:
        progress = "-".join(GESTURE_NAMES[g][0] for g in entered_gestures)
        pattern = "-".join(GESTURE_NAMES[g][0] for g in PASSWORD)
        oled.text("ENTER PASSWORD", 5, 5, 1)
        oled.text(f"Progress: {len(entered_gestures)}/{len(PASSWORD)}", 5, 20, 1)
        oled.text(f"Entered: {progress or '...'}", 5, 35, 1)
        oled.text(f"Pattern: {pattern}", 5, 50, 1)
    oled.show()

def process_gesture(gesture):
    global access_granted, last_action_time
    entered_gestures.append(gesture)
    last_action_time = time.monotonic()
    pixels.fill(GESTURE_COLORS[gesture])
    print(f"Gesture: {GESTURE_NAMES[gesture]}")
    time.sleep(0.2)
    clear_pixel()
    if entered_gestures == PASSWORD:
        access_granted = True
        pixels.fill((0, 255, 0))
        print("Access Granted!")
    elif len(entered_gestures) >= len(PASSWORD):
        print("Wrong Password!")
        oled.fill(0)
        oled.text("Wrong Password!", 10, 25, 1)
        oled.show()
        pixels.fill((255, 0, 0))
        time.sleep(2)
        reset_system()
    show_screen()

def process_buttons():
    global last_action_time
    if not access_granted:
        return
    if button_pressed(button_A):
        print("Button A - Locking system")
        reset_system()
    if button_pressed(button_B):
        print(f"Button B - Relay {'OFF' if relay_on else 'ON'}")
        set_relay(not relay_on)
        last_action_time = time.monotonic()
        show_screen()

reset_system()

while True:
    now = time.monotonic()
    process_buttons()
    if not access_granted:
        if entered_gestures and (now - last_action_time > GESTURE_TIMEOUT):
            print("Gesture timeout. Resetting.")
            reset_system()
    elif now - last_action_time > SESSION_TIMEOUT:
        print("Session expired. Locking.")
        reset_system()
    gesture = apds.gesture()
    if gesture in GESTURE_NAMES and not access_granted:
        process_gesture(gesture)
    time.sleep(0.1)
