import board
import array
import audiobusio
import neopixel
from ulab import numpy as np
from ulab import utils as ulab_utils

# --- Microphone setup ---
# Increase sample rate to capture up to ~32 kHz
mic = audiobusio.PDMIn(board.GP3, board.GP2, sample_rate=64000, bit_depth=16)
SAMPLE_SIZE = 256
samples = array.array('H', [0] * SAMPLE_SIZE)

# --- NeoPixel setup ---
num_pixels = 5
pixels = neopixel.NeoPixel(board.GP14, num_pixels, brightness=1, auto_write=False)

# --- Spectrum settings ---
FREQUENCY_BINS = num_pixels
MAX_MAGNITUDE = 5000  # Adjust based on mic sensitivity
MIN_MAGNITUDE = 1200
NOISE_GATE = 100

# FFT bin ranges (~6.4 kHz per LED)
# FFT resolution: 64 kHz / 256 = 250 Hz per bin
FREQ_RANGES = [
    (0, 25),      # 0–6.4 kHz
    (26, 51),     # 6.5–12.8 kHz
    (52, 77),     # 13–20 kHz
    (78, 103),    # 20–26 kHz
    (104, 128),   # 26–32 kHz
]

SPECTRUM_COLORS = [
    (255, 0, 255),    # Magenta
    (0, 0, 255),      # Blue
    (0, 255, 255),    # Cyan
    (0, 255, 0),      # Green
    (255, 255, 0),    # Yellow
]

peak_hold = [0] * num_pixels

# Sensitivity multiplier for each band (1.0 = default)
BAND_SENSITIVITY = [0.2, 0.2, 0.3, 0.8, 0.9]  
# You can tweak each value to make that band more or less responsive

# --- FFT-based spectrum computation ---
def spectrum_fft(samples):
    # Convert samples to float
    signal = np.array(samples, dtype=np.float)
    
    # Remove DC offset
    signal -= np.mean(signal)
    
    # Amplify weak signals
    signal *= 5.0
    
    # Apply Hamming window
    window = 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(len(signal)) / (len(signal) - 1))
    signal *= window
    
    # Compute FFT using spectrogram (ulab compatible)
    fft_power = ulab_utils.spectrogram(signal)
    magnitudes = np.sqrt(fft_power)  # Convert power to magnitude
    
    # Compute magnitudes per LED/bin
    freq_mag = []
    for i, (start_bin, end_bin) in enumerate(FREQ_RANGES):
        band_mag = int(np.sum(magnitudes[start_bin:end_bin]))
        band_mag = int(band_mag * BAND_SENSITIVITY[i])  # Apply sensitivity
        freq_mag.append(band_mag if band_mag > NOISE_GATE else 0)
    
    return freq_mag

# --- Map magnitude to LED brightness ---
def brightness_fast(mag):
    if mag <= MIN_MAGNITUDE:
        return 0
    if mag >= MAX_MAGNITUDE:
        return 255
    return ((mag - MIN_MAGNITUDE) * 255) // (MAX_MAGNITUDE - MIN_MAGNITUDE)

# --- Update NeoPixels ---
def display_fast(freq_mag):
    for i in range(num_pixels):
        mag = freq_mag[i]
        if mag > MIN_MAGNITUDE:
            led_bright = brightness_fast(mag)
            if led_bright > 5:
                r, g, b = SPECTRUM_COLORS[i]
                pixels[i] = ((r * led_bright) >> 8,
                             (g * led_bright) >> 8,
                             (b * led_bright) >> 8)
            else:
                pixels[i] = (0, 0, 0)
        else:
            pixels[i] = (0, 0, 0)
    pixels.show()

# --- Main loop ---
while True:
    try:
        mic.record(samples, len(samples))
        freq_mag = spectrum_fft(samples)

        # Peak hold with decay
        for i in range(FREQUENCY_BINS):
            if freq_mag[i] > peak_hold[i]:
                peak_hold[i] = freq_mag[i]
            else:
                peak_hold[i] = (peak_hold[i] * 230) >> 8
            freq_mag[i] = peak_hold[i]

        display_fast(freq_mag)
        print(freq_mag)

    except Exception as e:
        print("Error:", e)
        pixels.fill((255, 0, 0))
        pixels.show()


