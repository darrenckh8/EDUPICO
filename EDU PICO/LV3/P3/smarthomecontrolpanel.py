import time, json
import board, busio, digitalio, neopixel
import wifi, socketpool
import adafruit_ssd1306
from pwmio import PWMOut
from adafruit_motor import motor
from analogio import AnalogIn
from adafruit_httpserver import Server, Request, Response, POST

# Buttons
def setup_button(pin):
    btn = digitalio.DigitalInOut(pin)
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP
    return btn

button_sel = setup_button(board.GP0)
button_toggle = setup_button(board.GP1)

last_button_sel, last_sel_time = True, 0
last_button_toggle, last_toggle_time = True, 0

# Relay
relay = digitalio.DigitalInOut(board.GP22)
relay.direction = digitalio.Direction.OUTPUT

# NeoPixels
pixels = neopixel.NeoPixel(board.GP14, 2, brightness=0.2)

# OLED
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, busio.I2C(board.GP5, board.GP4))

# DC Motor
PWM_M2A, PWM_M2B = PWMOut(board.GP12, frequency=10000), PWMOut(board.GP13, frequency=10000)
dc_motor = motor.DCMotor(PWM_M2A, PWM_M2B)
dc_motor.throttle = 0.0

# Potentiometer
pot = AnalogIn(board.GP28)

WIFI_SSID, WIFI_PASSWORD = "", ""

def connect_wifi():
    while True:
        try:
            print("Connecting to Wi-Fi...")
            wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
            print(f"Connected! IP: {wifi.radio.ipv4_address}")
            return
        except Exception as e:
            print(f"Wi-Fi connection failed: {e}. Retrying in 2s...")
            time.sleep(2)

connect_wifi()
pool = socketpool.SocketPool(wifi.radio)

relay_on = motor_on = False
motor_throttle = web_throttle = pot_throttle = 0.0
throttle_source = "pot"  # "pot" or "web"
menu_items, selected_index = ['Relay', 'DC Motor'], 0
last_display_state = None

def update_motor_pixel(throttle, active):
    if not active:
        pixels[1] = (0, 0, 0); return
    if throttle < 0.5:
        r, g = int(2 * throttle * 255), 255
    else:
        r, g = 255, int(255 - 2 * (throttle - 0.5) * 510)
    pixels[1] = (r, g, 0)

def update_oled():
    oled.fill(0)
    oled.text("Smart Home Panel", 10, 0, 1)
    for i, item in enumerate(menu_items):
        prefix = '>' if i == selected_index else ' '
        state = 'ON' if (relay_on if i == 0 else motor_on) else 'OFF'
        oled.text(f"{prefix} {item}: {state}", 0, 15 + i*15, 1)
    oled.text(f"Throttle: {int(motor_throttle*100)}%", 0, 50, 1)
    oled.show()

def toggle_relay(source="button"):
    global relay_on
    relay_on = not relay_on
    relay.value = relay_on
    pixels[0] = (0, 255, 0) if relay_on else (0, 0, 0)
    update_motor_pixel(motor_throttle, motor_on)
    print(f"Relay toggled to: {'ON' if relay_on else 'OFF'} ({source})")
    update_oled()

def toggle_motor(source="button"):
    global motor_on
    motor_on = not motor_on
    update_motor_pixel(motor_throttle, motor_on)
    print(f"DC Motor toggled to: {'ON' if motor_on else 'OFF'} ({source})")
    update_oled()

def get_html():
    return f"""<!DOCTYPE html>
<html>
<head><title>Smart Home Control</title></head>
<body>
<h2>Smart Home Control Panel</h2>
<form method='POST'>
<p><b>Relay</b> <button type='submit' name='action' value='relay_toggle'>Toggle</button></p>
<p><b>DC Motor</b> <button type='submit' name='action' value='motor_toggle'>Toggle</button></p>
</form>
<p>Relay State: <b id='relay_state'>{'ON' if relay_on else 'OFF'}</b></p>
<p>DC Motor State: <b id='motor_state'>{'ON' if motor_on else 'OFF'}</b></p>
<p>DC Motor Throttle: <b id='motor_throttle'>{int(motor_throttle*100)}%</b></p>
<p>Throttle Source: <b id='throttle_source'>{throttle_source}</b></p>
<p>Set Throttle:
    <input type="range" min="0" max="100" value="{int(web_throttle*100)}" id="throttle_slider">
    <span id="slider_val">{int(web_throttle*100)}</span>%
</p>
<script>
let slider = document.getElementById('throttle_slider');
let sliderVal = document.getElementById('slider_val');
slider.oninput = () => sliderVal.textContent = slider.value;
slider.onchange = () => fetch('/', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
    body: 'action=throttle_set&throttle=' + slider.value
}}).then(_ => updateStates());
function updateStates() {{
    fetch('/status').then(r => r.json()).then(data => {{
        document.getElementById('relay_state').textContent = data.relay;
        document.getElementById('motor_state').textContent = data.motor;
        document.getElementById('motor_throttle').textContent = data.throttle + '%';
        document.getElementById('throttle_source').textContent = data.throttle_source;
        slider.value = data.slider_value;
        sliderVal.textContent = data.slider_value;
    }});
}}
setInterval(updateStates, 500);
</script>
</body>
</html>"""

server = Server(pool, "/static")

@server.route("/status")
def status(request: Request):
    return Response(request, json.dumps({
        "relay": "ON" if relay_on else "OFF",
        "motor": "ON" if motor_on else "OFF",
        "throttle": int(motor_throttle * 100),
        "throttle_source": throttle_source,
        "web_throttle": int(web_throttle * 100),
        "slider_value": int(motor_throttle * 100)
    }), content_type='application/json')

@server.route("/")
def base(request: Request):
    return Response(request, get_html(), content_type='text/html')

@server.route("/", POST)
def buttonpress(request: Request):
    global selected_index, web_throttle, throttle_source
    raw_text = request.raw_request.decode("utf8")
    if "relay_toggle" in raw_text: toggle_relay("web"); selected_index = 0
    elif "motor_toggle" in raw_text: toggle_motor("web"); selected_index = 1
    elif "throttle_set" in raw_text:
        try:
            val = int(request.form_data["throttle"])
            web_throttle, throttle_source = max(0, min(100, val)) / 100.0, "web"
        except Exception as e:
            print("Throttle set error:", e)
    return Response(request, get_html(), content_type='text/html')

server.start(str(wifi.radio.ipv4_address), port=80)
print(f"Server running at: http://{wifi.radio.ipv4_address}")

def handle_buttons(now):
    global last_button_sel, last_sel_time, selected_index
    global last_button_toggle, last_toggle_time

    # Selection button
    if not button_sel.value and last_button_sel and (now - last_sel_time > 0.25):
        selected_index = (selected_index + 1) % len(menu_items)
        update_oled(); last_sel_time = now
    last_button_sel = button_sel.value

    # Toggle button
    if not button_toggle.value and last_button_toggle and (now - last_toggle_time > 0.25):
        toggle_relay("button") if selected_index == 0 else toggle_motor("button")
        last_toggle_time = now
    last_button_toggle = button_toggle.value

def handle_motor():
    global motor_throttle, pot_throttle, web_throttle, throttle_source
    raw = pot.value / 65535
    pot_new = 0 if raw < 0.05 else raw
    if abs(pot_new - pot_throttle) > 0.03: throttle_source = "pot"
    pot_throttle = pot_new
    motor_throttle = web_throttle if throttle_source == "web" else pot_throttle
    dc_motor.throttle = motor_throttle if motor_on else 0.0
    update_motor_pixel(motor_throttle, motor_on)
    pixels[0] = (0, 255, 0) if relay_on else (0, 0, 0)

def handle_wifi():
    if not wifi.radio.connected:
        print("Wi-Fi lost. Reconnecting..."); connect_wifi()

def handle_server():
    try: server.poll()
    except OSError as e:
        if not (hasattr(e, 'errno') and e.errno == 32): print(">>> SERVER ERROR <<<", e)

def handle_oled():
    global last_display_state
    state = (selected_index, relay_on, motor_on, int(motor_throttle * 100))
    if state != last_display_state:
        update_oled(); last_display_state = state

try:
    while True:
        now = time.monotonic()
        handle_buttons(now)
        handle_motor()
        handle_wifi()
        handle_server()
        handle_oled()
        time.sleep(0.02)
except Exception as e:
    print(">>> FATAL ERROR <<<", e)

