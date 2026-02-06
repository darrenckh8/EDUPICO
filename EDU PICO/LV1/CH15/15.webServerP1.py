import board
import digitalio
import wifi
import socketpool
from adafruit_httpserver import Server, Request, Response, POST

# Setup WiFi Access Point
wifi.radio.start_ap(ssid="EDUPICO_AP", password="12345678")
pool = socketpool.SocketPool(wifi.radio)

# Setup Relay
relay = digitalio.DigitalInOut(board.GP22)
relay.direction = digitalio.Direction.OUTPUT

# HTML webpage
html = """<!DOCTYPE html>
<html>
<head>
<title>USB Relay Control</title>
</head>
<body>
<p>USB Relay Light Control</p>
<form accept-charset="utf-8" method="POST">
<button class="button" name="Light On" value="light_on" type="submit">Light On</button>
<button class="button" name="Light Off" value="light_off" type="submit">Light Off</button>
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
    if "light_on" in raw_text:
        print("Light ON")
        relay.value = True
    elif "light_off" in raw_text:
        print("Light OFF")
        relay.value = False
    return Response(request, html, content_type='text/html')

print("Starting server...")
server.start(str(wifi.radio.ipv4_address_ap), port=80)
print("Listening on http://%s" % wifi.radio.ipv4_address_ap)

try:
    while True:
        server.poll()
except Exception as e:
    print(">>> ERROR <<<")
    print(e)