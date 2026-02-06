import board
import digitalio
import wifi
import socketpool
from adafruit_httpserver import Server, Request, Response, POST

# WiFi credentials
WIFI_SSID = ""
WIFI_PASSWORD = ""

# Connect to WiFi
print("Connecting to Wi-Fi...")
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
print(f"Connected! IP: {wifi.radio.ipv4_address}")
pool = socketpool.SocketPool(wifi.radio)

# Setup relay
relay = digitalio.DigitalInOut(board.GP22)
relay.direction = digitalio.Direction.OUTPUT


# HTML webpage
html = """<!DOCTYPE html>
<html>
<head><title>USB Relay Control</title></head>
<body>
<h2>USB Relay Light Control</h2>
<form method="POST">
<button type="submit" name="action" value="light_on">Light On</button>
<button type="submit" name="action" value="light_off">Light Off</button>
</form>
</body>
</html>"""

# Setup server
server = Server(pool, "/static")

@server.route("/")
def base(request: Request):
    return Response(request, html, content_type='text/html')

@server.route("/", POST)
def buttonpress(request: Request):
    raw_text = request.raw_request.decode("utf8")
    if "action=light_on" in raw_text:
        print("Light ON")
        relay.value = True
    elif "action=light_off" in raw_text:
        print("Light OFF")
        relay.value = False
    return Response(request, html, content_type='text/html')

server.start(str(wifi.radio.ipv4_address), port=80)
print(f"Server running at: http://{wifi.radio.ipv4_address}")

try:
    while True:
        server.poll()
except Exception as e:
    print(">>> ERROR <<<")
    print(e)