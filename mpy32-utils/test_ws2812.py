import machine
import time
import neopixel as nx

# LED strip configuration
# number of pixels
num_pixels = 300
# strip control gpio
strip_pin = 5

np = nx.NeoPixel(machine.Pin(strip_pin), num_pixels)
led = machine.Pin(2, machine.Pin.OUT)


def light_full(color):
    np.fill(color)
    np.write()


COLORS = [(0, 0, 0)] + \
    [(n * 4, 0, 0) for n in range(32)] + \
    [(0, n * 4, 0) for n in range(32)] + \
    [(0, 0, n * 4) for n in range(32)] + \
    [(0, 0, 0)] * 3

for c in COLORS:
    led.value(1)
    light_full(c)
    led.value(0)
    time.sleep(.1)
