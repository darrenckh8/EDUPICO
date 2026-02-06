import board
import time
import digitalio
import simpleio

button_A = digitalio.DigitalInOut(board.GP0)
button_A.direction = digitalio.Direction.INPUT
button_A.pull = digitalio.Pull.UP

button_B = digitalio.DigitalInOut(board.GP1)
button_B.direction = digitalio.Direction.INPUT
button_B.pull = digitalio.Pull.UP

buzzer_pin = board.GP21

NOTES = {
    "C": 523,
    "D": 587,
    "E": 659,
    "F": 698,
    "G": 784,
    "A": 880,
    "B": 988,
    "C_high": 1047,
    "silence": 0
}

print("Buzzer Control System!")
print("Button A: Doorbell sound")
print("Button B: Play a musical scale")

def play_doorbell():
    print(f"Ding-dong! Someone's at the door!")
    simpleio.tone(buzzer_pin, NOTES["G"], 0.5)
    simpleio.tone(buzzer_pin, NOTES["C"], 0.8)
    simpleio.tone(buzzer_pin, NOTES["silence"], 0.2)

def play_scale():
    print(f"Playing musical scale!")
    scale_notes = ["C", "D", "E", "F", "G"]
    for note in scale_notes:
        print(f"   Playing note: {note}")
        simpleio.tone(buzzer_pin, NOTES[note], 0.5)
        time.sleep(0.1)
    simpleio.tone(buzzer_pin, NOTES["silence"], 0.3)

while True:
    if not button_A.value:
        play_doorbell()
        time.sleep(0.5)
    elif not button_B.value:
        play_scale()
        time.sleep(0.5)
    time.sleep(0.1)
