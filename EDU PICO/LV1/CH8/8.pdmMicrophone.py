import board
import time
import array
import math
import audiobusio
import neopixel

mic = audiobusio.PDMIn(board.GP3, board.GP2, sample_rate=16000, bit_depth=16)
samples = array.array('H', [0] * 1024)

num_pixels = 1
pixel_pin = board.GP14
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2)
pixels.fill((0, 0, 0))

def log10(x):
    return math.log(x) / math.log(10)

def normalized_rms(values):
    minbuf = sum(values) / len(values)
    samples_sum = sum(float(sample - minbuf) * (sample - minbuf) for sample in values)
    return math.sqrt(samples_sum / len(values))

CLAP_THRESHOLD = 60
CLAP_TIME_WINDOW = 2
last_clap_time = 0
clap_count = 0
led_on = False

while True:
    mic.record(samples, len(samples))
    magnitude = normalized_rms(samples)
    
    if magnitude > 0:
        sound_level_dB = 20 * log10(magnitude)
        print(f"Sound Level(dB): {sound_level_dB:.2f}")
        
        if sound_level_dB > CLAP_THRESHOLD:
            current_time = time.monotonic()
            
            if current_time - last_clap_time < CLAP_TIME_WINDOW:
                clap_count += 1
            else:
                clap_count = 1
            
            last_clap_time = current_time
            
            if clap_count == 2:
                led_on = not led_on
                pixels.fill((255, 255, 255) if led_on else (0, 0, 0))
                print("Double Clap Detected! Toggling NeoPixel")
                clap_count = 0
    
    time.sleep(0.01)
