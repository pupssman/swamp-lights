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


class Scene:
    """
    intro, outro and loop are sequences of frames
    frame is sequence of tuples (color, length) where color is rgb
    """
    def __init__(self, intro=[], loop=[], outro=[]):
        self.intro = intro
        self.outro = outro
        self.loop = loop


SCENE_DARKNESS = Scene(loop=[((0, 0, 0), 150)])  # just black
SCENE_COZY = Scene(
    intro=[
        ((x, x, 0), 20)
        for x in range(0, 100, 5)
    ],
    loop=[
        ((100, 100, 0), 20),
        ((110, 100, 0), 20),
        ((120, 100, 0), 20),
        ((130, 100, 0), 20),
        ((140, 100, 0), 20),
        ((150, 100, 0), 20),
        ((140, 100, 0), 20),
        ((130, 100, 0), 20),
        ((120, 100, 0), 20),
        ((110, 100, 0), 20),
    ], outro=[
        ((x, x, 0), 20)
        for x in range(100, 0, -5)
    ],
)  # in room 1 and 2
SCENE_PSYCHO = Scene()  # in room 1 and 2
SCENE_WALKER = Scene()  # in room 3
SCENE_TREE = Scene()  # in room 4


class State:
    def __init__(self):
        self.scene = SCENE_DARKNESS
        self.to_scene = None
        self.period = 0.1
        self.max_pixels = 150  # max pixels
        self.np = nx.NeoPixel(machine.Pin(strip_pin), self.max_pixels)

    def change_state(self, to_state):
        # FIXME: change properly
        if to_state == 0:  # initial
            self.to_scene = SCENE_DARKNESS
        elif to_state == 1:  # primary
            self.to_scene = SCENE_COZY
        elif to_state == 2:  # scene high
            self.to_scene = SCENE_PSYCHO
        else:
            pass
            # FIXME other roles

    def play_one(self, sequence):
        for frame in sequence:
            time.sleep(self.period)
            self.show_frame(frame)
        else:
            time.sleep(self.period)

    def show_frame(self, frame):
        # frame is sequence of (color, length)
        n = 0
        for (color, length) in frame:
            for i in range(length):
                self.np[n] = color
                n += 1

    def play(self):
        if self.to_scene:
            self.play_one(self.scene.outro)
            self.play_one(self.to_scene.intro)
            self.scene = self.to_scene
            self.to_scene = None
        else:
            self.play_one(self.scene.loop)


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
