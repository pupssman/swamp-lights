import machine
import time
import neopixel as nx
import urequests
import ubinascii
import _thread

# unique id is 4 bytes, get nicer repr
DID = ubinascii.hexlify(machine.unique_id()).decode('utf-8')

# FIXME: read those from drive?
HOST = '192.168.0.24'
PORT = 5000
SSID = 'wood_wonders'
PWD = 'askthechildren'

# LED strip configuration
# we have 18 bulbs with 7 pixels and 1, last, with 6 pixels
# just disregard the 19th missing pixel, should do no harm
num_bulbs = 19
num_pixels = 7 * num_bulbs
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


def make_wave_loop(width=2, interval=3):
    # starting from 1, duh :(
    blocks = [
        (3,),
        (4, 10),
        (5, 9),
        (6, 8),
        (7,),
        (11, 17),
        (12, 16),
        (13, 15),
        (14,)
    ]

    starts, ends = (0, 1), (17, 18)

    # start with all red
    background = ['r'] * num_bulbs

    # starts and ends are blue
    for i in starts:
        background[i] = 'b'
    for i in ends:
        background[i] = 'b'

    mask = []

    # mask is the color seq of blocks
    while len(mask) < len(blocks):
        mask.append('b' * width)  # up of the wave -- blue -- you can pass
        mask.append('r' * interval)  # down of the wave -- red -- you can not

    mask = ''.join(mask)

    result = []
    for n in range(width + interval):  # max phases -- sum of widht + period
        # n is the phase
        result.append(list(background))

        # push relevant color for matching block
        for bis, c in zip(blocks, mask):
            for bi in bis:
                result[-1][bi - 1] = c

        # rotate mask once to the right, propagate the wave
        mask = mask[-1:] + mask[:-1]

    return [''.join(loop) for loop in result]


# before 3 min
LOOP_EASY = make_wave_loop(width=2, interval=3)

# after 3 min
LOOP_HARD = make_wave_loop(width=1, interval=4)

# just all red
LOOP_IDLE = ['r' * num_bulbs]


def light_bulbs(bulbseq, intensity=31, bulb_size=7):
    """
    lights bulbs as given
    bubseq: a string of r/g/b/k for bulb color
    intensity: from 0 to 31, duh
    """

    podgon = 0  # dead pixels at the start
    # clone pixels -- these repeat previous, dont write them separately
    skips = {7 * 2 - 1, 7 * 3 - 1, 7 * 10 - 1}
    start = podgon  # start from deat pixels
    backoff = 0

    for c in bulbseq:
        color = cmap[c][intensity]
        for i in range(bulb_size):
            if start + i >= num_pixels:
                break
            if start + i in skips:
                backoff += 1  # that duplicate bulb, just dont use it
            else:
                # print('writing to %d color %s' % (start + i - backoff, c))
                np[start + i - backoff] = color
        start += bulb_size  # here goes next bulb
    np.write()


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

        for _ in range(5):
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
        self.loop = LOOP_EASY
        self.speed = 1  # 1 for normal, less for faster, more for slower

    def change_state(self, to_state):
        # FIXME: change properly
        if to_state == 999:
            self.loop = LOOP_HARD
        else:
            self.loop = LOOP_EASY

    def on_internal_problem(self):
        # FIXME: good only for dev
        self.loop = LOOP_EASY

    def play_loop(self):
        for c in self.loop:
            light_bulbs(c)
            time.sleep(5 * self.speed)

            for n in range(5):
                light_bulbs(c, intensity=20)
                time.sleep(0.2 * self.speed)
                light_bulbs(c, intensity=30)
                time.sleep(0.2 * self.speed)


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
        STATE.play_loop()
