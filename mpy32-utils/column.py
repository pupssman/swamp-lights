import time

from common import Connector, Blinker, ButtonTracker, Scene, ScenePlayer

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


SCENE_BASE = make_loop_scene((25, 100, 50), 0.7, 50, 10, 10)
SCENE_DANGER = make_loop_scene((100, 0, 20), 0.5, 10, 5, 5)
SCENE_ALARM = make_loop_scene((150, 30, 0), 0.5, 50, 30, 10)


class State:
    def __init__(self):
        self.player = ScenePlayer(initial_scene=SCENE_DARKNESS, on_frame=self.on_frame)
        self.state = -1
        self.raise_time = None
        self.time_limit = 10  # seconds?
        self.exploded = False
        self.connector = None

    def on_frame(self):
        # check if timer is expired
        if not self.exploded and \
                self.raise_time is not None and \
                time.time() - self.raise_time > self.time_limit:
            self.exploded = True
            self.player.change_scene(SCENE_ALARM)
            if self.connector:
                self.connector.report_event(eid=15)

    def handle_column(self, is_raised):
        """
         is_raised is when column is raised to the top
            -- danger mode with countdown
        """
        if self.exploded:
            return  # already exploded, nothing to do
        if is_raised:
            self.raise_time = time.time()
            print('column is raised!')
            self.player.change_scene(SCENE_DANGER)
        else:
            self.raise_time = None
            print('colum is released')
            self.player.change_scene(SCENE_BASE)

    def change_state(self, to_state):
        if to_state != self.state or self.exploded and to_state == 0:
            self.state = to_state

            if to_state == 0:  # initial
                self.player.change_scene(SCENE_DARKNESS)
                self.exploded = False
                self.raise_time = None
            elif to_state == 1:  # primary
                self.player.change_scene(SCENE_BASE)
            elif to_state == 2:  # scene high
                self.player.change_scene(SCENE_DANGER)
            else:
                self.player.change_scene(SCENE_ALARM)

    def play(self):
        return self.player.play()


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
    STATE.connector = connector

    while True:
        STATE.play()
