import time
import os 
import board
import digitalio
import audiomp3
import audiopwmio

buttonA = digitalio.DigitalInOut(board.GP0)
buttonA.direction = digitalio.Direction.INPUT
buttonA.pull = digitalio.Pull.UP

buttonB = digitalio.DigitalInOut(board.GP1)
buttonB.direction = digitalio.Direction.INPUT
buttonB.pull = digitalio.Pull.UP

dac = audiopwmio.PWMAudioOut(left_channel=board.GP20, right_channel=board.GP21)

song_array = [file for file in os.listdir("/music") if file.endswith(".mp3")]
song_array.sort()

if not song_array:
    print("No MP3 files found in /music folder.")
    while True:
        pass

counter = 0
playing = False

def load_mp3(file_name):
    return audiomp3.MP3Decoder(open("/music/" + file_name, "rb"))

def check_button(button):
    if not button.value:
        time.sleep(0.05)
        while not button.value:
            time.sleep(0.01)
        return True
    return False

print("Button A: Play/Stop | Button B: Next Track")

while True:
    if check_button(buttonA):
        if not playing:
            print(f"Playing: {song_array[counter]}")
            dac.play(load_mp3(song_array[counter]), loop=False)
            playing = True
        else:
            print("Stopped")
            dac.stop()
            playing = False
        time.sleep(0.3)

    if check_button(buttonB):
        dac.stop()
        counter = (counter + 1) % len(song_array)
        print(f"Next: {song_array[counter]}")
        dac.play(load_mp3(song_array[counter]), loop=False)
        playing = True
        time.sleep(0.3)
