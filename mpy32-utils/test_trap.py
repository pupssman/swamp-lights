import machine
import time
import neopixel as nx
import urequests
import ubinascii
import _thread

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
strip_pin = 2
button_pin = 5  # dp 5 to read button
np = nx.NeoPixel(machine.Pin(strip_pin), num_pixels)
led = machine.Pin(2, machine.Pin.OUT)
# it should be locked on gnd,
button = machine.Pin(button_pin, machine.Pin.IN, machine.Pin.PULL_UP)

# FIXME: somehow colors are messed, names should be correct
G = [(n * 7, 0, 0) for n in range(32)]
R = [(0, n * 7, 0) for n in range(32)]
B = [(0, 0, n * 7) for n in range(32)]
K = [(0, 0, 0)] * 3

cmap = {'r': R, 'b': B, 'g': G, 'k': K[:1] * 32}  # color letter to list of 32


# 3 colors cycled
LOOP_A = [
    'rgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgb',
    'gbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbr',
    'brgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrgbrg',
]

# g or b then black
LOOP_B = [
    'rb' * 22,
    'br' * 22,
    'kk' * 22,
]


def light_bulbs(bulbseq, intensity=31, bulb_size=7):
    """
    lights bulbs as given
    bubseq: a string of r/g/b/k for bulb color
    intensity: from 0 to 31, duh
    """

    podgon = 6
    skipbulbs = 37

    for n, c in enumerate(bulbseq):
        start = podgon + n * bulb_size
        if n > skipbulbs:
            color = cmap[c][intensity]
        else:
            color = (0, 0, 0)  # fixme
        for i in range(bulb_size):
            if start + i >= num_pixels:
                break
            np[start + i] = color
    np.write()


def play_loop(loop):
    for c in loop:
        light_bulbs(c)
        time.sleep(3)


def do_connect():
    """
    will try to connect for at most 30 secs
    will raise Exceptionif not connected
    """
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(SSID, PWD)

        for _ in range(30):
            # 30 seconds to connect
            if not wlan.isconnected():
                time.sleep(1)
            else:
                break  # from for loop
        else:
            # did not break
            raise Exception('did not connect after 30 secs')

    print('network config:', wlan.ifconfig())


def register():
    res = urequests.get('http://%s:%s/hello?did=%s' % (HOST, PORT, DID))
    print(res.text)


def get_state():
    res = urequests.get('http://%s:%s/state?did=%s' % (HOST, PORT, DID))
    print(res.text)
    return int(res.text)


def report_event(eid):
    res = urequests.post('http://%s:%s/event?did=%s&eid=%d' %
                         (HOST, PORT, DID, eid))
    print(res.text)


class State:
    def __init__(self):
        self.loop = LOOP_A

    def change_state(self, to_state):
        # FIXME: change properly
        if to_state == 999:
            self.loop = LOOP_B
        else:
            self.loop = LOOP_A

    def on_internal_problem(self):
        # FIXME: good only for dev
        self.loop = LOOP_B


STATE = State()


def button_interrupt(pin_irq):
    # FIXME: god knows whats in these args
    print('button pressed: %s' % pin_irq)
    report_event(999)  # debug event


def check_for_state(delay):
    "threadfunc"
    print('check for state thread started')

    while True:
        time.sleep(delay)  # check for state each second
        try:
            new_state_code = get_state()
            STATE.change_state(new_state_code)
        except Exception as e:
            print('oops: %s' % e)


if __name__ == '__main__':
    # 3 is like machine.Pin.IRQ_RISING but for both (rising / falling)
    button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_interrupt)

    try:
        do_connect()
        register()
    except Exception:
        # failed to connect / register, play the dead loop
        STATE.on_internal_problem()

    _thread.start_new_thread(check_for_state, (1,))

    while True:
        play_loop(STATE.loop)
