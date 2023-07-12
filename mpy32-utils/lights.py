import time
import machine
import neopixel as nx

from common import Connector, Blinker

# strip control gpio
strip_pin = 4


class Scene:
    """
    intro, outro and loop are sequences of frames
    frame is sequence of tuples (color, length) where color is rgb
    """
    def __init__(self, intro=[], loop=[], outro=[]):
        self.intro = intro
        self.outro = outro
        self.loop = loop


SCENE_DARKNESS = Scene(loop=[[((0, 0, 0), 150)]])  # just black
SCENE_COZY = Scene(
    intro=[
        [((2 * x, x, 0), 20)]
        for x in range(0, 100, 5)
    ],
    loop=[
        [((200, 100, 0), 20)],
        [((210, 100, 0), 20)],
        [((220, 100, 0), 20)],
        [((230, 100, 0), 20)],
        [((240, 100, 0), 20)],
        [((250, 100, 0), 20)],
        [((240, 100, 0), 20)],
        [((230, 100, 0), 20)],
        [((220, 100, 0), 20)],
        [((210, 100, 0), 20)],
    ], outro=[
        [((x, x, 0), 20)]
        for x in range(100, 0, -5)
    ],
)  # in room 1 and 2
SCENE_PSYCHO = Scene(
    intro=[
        [((x, 0, 2 * x), 150)]
        for x in range(0, 20, 2)
    ],
    loop=[
        [((80 + x, 0, 200 - x), 150)]
        for x in list(range(0, 20, 1)) + list(range(20, 0, -1))
    ]
)  # in room 1 and 2
SCENE_WALKER = Scene()  # in room 3
SCENE_TREE = Scene()  # in room 4


class State:
    def __init__(self):
        self.state = -1
        self.scene = SCENE_PSYCHO  # FIXME: just testing
        self.to_scene = None
        self.period = 0.2
        self.max_pixels = 150  # max pixels
        self.np = nx.NeoPixel(machine.Pin(strip_pin), self.max_pixels)

    def change_state(self, to_state):
        if to_state != self.state:
            self.state = to_state

            # FIXME: change properly
            if to_state == 0:  # initial
                self.to_scene = SCENE_COZY
            elif to_state == 1:  # primary
                self.to_scene = SCENE_COZY
            elif to_state == 2:  # scene high
                self.to_scene = SCENE_PSYCHO
            else:
                self.to_scene = SCENE_PSYCHO

    def play_one(self, sequence):
        for frame in sequence:
            time.sleep(self.period)
            self.show_frame(frame)
        else:
            time.sleep(self.period)

    def show_frame(self, frame):
        # frame is sequence of (color, length)
        n = 0
        print('showing frame %s' % (frame,))
        for (color, length) in frame:
            r, g, b = color
            # cap the colors just in case
            cw = min(g, 150), min(r, 150), min(b, 150)
            print('showing color %s' % (cw,))

            for i in range(length):
                self.np[n] = cw
                n += 1
        self.np.write()

    def play(self):
        if self.to_scene:
            print('switching scene')
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
        STATE.play()
