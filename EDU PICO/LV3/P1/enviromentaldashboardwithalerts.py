import time
import ssl
import socketpool
import wifi
import adafruit_requests
import microcontroller
import board
import busio
import adafruit_ahtx0
import audiobusio
import array
import math
import adafruit_ssd1306
from adafruit_apds9960.apds9960 import APDS9960

# ========= WiFi =========
SSID = "mmchyy"
PASSWORD = "mm001971"

print("Connecting to WiFi...")
wifi.radio.connect(SSID, PASSWORD)
print("Connected! IP:", wifi.radio.ipv4_address)

# ========= InfluxDB Cloud =========
ORG = ""
BUCKET = ""
TOKEN = ""
URL = "https://us-east-1-1.aws.cloud2.influxdata.com/api/v2/write"

WRITE_URL = f"{URL}?org={ORG}&bucket={BUCKET}&precision=s"
HEADERS = {
    "Authorization": "Token " + TOKEN,
    "Content-Type": "text/plain; charset=utf-8"
}

# ========= Setup Requests =========
pool = socketpool.SocketPool(wifi.radio)
session = adafruit_requests.Session(pool, ssl.create_default_context())

# ========= Sensor Setup =========
i2c = busio.I2C(board.GP5, board.GP4)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
AHT_sensor = adafruit_ahtx0.AHTx0(i2c)
apds = APDS9960(i2c)
apds.enable_color = True

mic = audiobusio.PDMIn(board.GP3, board.GP2, sample_rate=16000, bit_depth=16)
samples = array.array('H', [0] * 1024)


def log10(x):
    return math.log(x) / math.log(10)


def normalized_rms(values):
    minbuf = sum(values) / len(values)
    samples_sum = sum(float(sample - minbuf) * (sample - minbuf)
                      for sample in values)
    return math.sqrt(samples_sum / len(values))


# ========= Send Loop =========
while True:
    # Internal CPU temperature
    cpu_temp = microcontroller.cpu.temperature

    # AHT20 temperature and humidity
    temperature = AHT_sensor.temperature
    humidity = AHT_sensor.relative_humidity

    # Sound level (PDM mic, dB)
    mic.record(samples, len(samples))
    magnitude = normalized_rms(samples)
    sound_level_dB = 20 * log10(magnitude) if magnitude > 0 else 0

    # Light sensor (APDS9960, clear channel)
    r, g, b, c = apds.color_data
    light_level = c

    print(f"CPU Temp: {cpu_temp:.2f} | Temp: {temperature:.2f} | Humidity: {humidity:.2f} | Sound(dB): {sound_level_dB:.2f} | Light: {light_level}")

    oled.fill(0)
    oled.text(f"Temp: {temperature:.1f}C", 0, 0, 1)
    oled.text(f"Hum: {humidity:.1f}%", 0, 12, 1)
    oled.text(f"Sound: {sound_level_dB:.1f}dB", 0, 24, 1)
    oled.text(f"Light: {light_level}", 0, 36, 1)
    oled.text(f"CPU: {cpu_temp:.1f}C", 0, 48, 1)
    oled.show()

    # InfluxDB line protocol
    data = f"environment,device=picoWH cpu_temp={cpu_temp:.2f},temp={temperature:.2f},humidity={humidity:.2f},light_level={float(light_level):.2f}"

    try:
        response = session.post(WRITE_URL, data=data, headers=HEADERS)
        print("InfluxDB response:", response.status_code)
        response.close()
    except Exception as e:
        print("Error sending to InfluxDB:", e)

    time.sleep(1)
