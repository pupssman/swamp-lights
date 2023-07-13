import time
import machine
import neopixel as nx

from common import Connector, Blinker, DID, DID_ENTRY, ButtonTracker

if DID == DID_ENTRY:
    # FIXME: oh hell
    strip_pin = 2
else:
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


L = 100
SCENE_DARKNESS = Scene(loop=[[((0, 0, 0), L)]])  # just black


def make_loop_scene(base_color, pulse_depth, pulse_period, intro_size, outro_size):
    r, g, b = base_color

    def scale(a):
        return (int(r*a), int(g*a), int(b*a))

    return Scene(
        intro=[
            [(scale(float(x) / intro_size), L)]
            for x in range(0, intro_size)
        ], loop=[
            [(scale(float(x) / pulse_period), L)]
            for x in list(range(int(pulse_period * pulse_depth), pulse_period))
            + list(range(pulse_period, int(pulse_period * pulse_depth), -1))
        ], outro=[
            [(scale(float(x) / outro_size), L)]
            for x in range(outro_size, 0, -1)
        ],
    )  # in room 1 and 2


SCENE_BASE = make_loop_scene((25, 100, 50), 0.8, 50, 10, 10)
SCENE_DANGER = make_loop_scene((100, 50, 20), 0.5, 10, 5, 5)
SCENE_ALARM = make_loop_scene((150, 0, 0), 0.8, 50, 10, 10)


class State:
    def __init__(self):
        self.state = -1
        self.scene = SCENE_DARKNESS  # FIXME: just testing
        self.to_scene = None
        self.period = 0.1
        self.max_pixels = 150  # max pixels
        self.np = nx.NeoPixel(machine.Pin(strip_pin), self.max_pixels)

    def handle_column(self, is_raised):
        """
         is_raised is when column is raised to the top
            -- danger mode with countdown
        """
        if is_raised:
            print('column is raised!')
            self.to_scene = SCENE_DANGER
        else:
            print('colum is released')
            self.to_scene = SCENE_BASE

    def change_state(self, to_state):
        if to_state != self.state:
            self.state = to_state

            # FIXME: change properly
            if to_state == 0:  # initial
                self.to_scene = SCENE_DARKNESS
            elif to_state == 1:  # primary
                self.to_scene = SCENE_BASE
            elif to_state == 2:  # scene high
                self.to_scene = SCENE_DANGER
            else:
                self.to_scene = SCENE_ALARM

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
    print('Beginning column')
    blink = Blinker()

    def on_state_callback(sid):
        print('Got new state %s' % sid)
        return STATE.change_state(sid)

    BTN_B = ButtonTracker(
        pin=14,
        # when column is raised pin is grounded -> it is on low
        on_high=lambda: STATE.handle_column(is_raised=False),
        on_low=lambda: STATE.handle_column(is_raised=True))

    connector = Connector(blink, on_state=on_state_callback)
    connector.begin()

    while True:
        STATE.play()
