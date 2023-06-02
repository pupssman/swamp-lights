import machine
import time
import neopixel as nx
import urequests
import ubinascii

# unique id is 4 bytes, get nicer repr
DID = ubinascii.hexlify(machine.unique_id()).decode('utf-8')

# FIXME: read those from drive?
HOST = '192.168.0.2'
PORT = 5000
SSID = ''
PWD = ''

# LED strip configuration
# number of pixels
num_pixels = 300
# strip control gpio
strip_pin = 5
np = nx.NeoPixel(machine.Pin(strip_pin), num_pixels)
led = machine.Pin(2, machine.Pin.OUT)


def light_full(color):
    for n in range(num_pixels):
        np[n] = color
    # np.fill(color)
    np.write()


G = [(n * 4, 0, 0) for n in range(32)]
B = [(0, n * 4, 0) for n in range(32)]
R = [(0, 0, n * 4) for n in range(32)]
K = [(0, 0, 0)] * 3

RED_LOOP = K + R + R[::-1] + K

GREEN_LOOP = K + G + G[::-1] + K


def play_loop(loop):
    for c in loop:
        light_full(c)
        time.sleep(.05)


def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(SSID, PWD)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())


def register():
    res = urequests.get('http://%s:%s/hello?did=%s' % (HOST, PORT, DID))
    print(res.text)


def get_state():
    res = urequests.get('http://%s:%s/state?did=%s' % (HOST, PORT, DID))
    print(res.text)
    return int(res.text)


do_connect()
register()
loop = GREEN_LOOP

while True:
    state = get_state()
    if state == 999:  # debug
        loop = RED_LOOP
    else:
        loop = GREEN_LOOP

    play_loop(loop)
