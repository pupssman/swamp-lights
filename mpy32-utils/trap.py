import time
import machine
import neopixel as nx

from common import Connector, Blinker

# LED strip configuration
# we have 18 bulbs with 7 pixels and 1, last, with 6 pixels
# just disregard the 19th missing pixel, should do no harm
num_bulbs = 19
num_pixels = 7 * num_bulbs
# strip control gpio
strip_pin = 4
np = nx.NeoPixel(machine.Pin(strip_pin), num_pixels)

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


if __name__ == '__main__':
    print('Beginning trap')
    blink = Blinker()

    def on_state_callback(sid):
        print('Got new state %s' % sid)
        return STATE.change_state(sid)

    connector = Connector(blink, on_state=on_state_callback)
    connector.begin()

    while True:
        STATE.play_loop()
