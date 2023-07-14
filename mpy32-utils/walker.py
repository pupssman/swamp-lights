from common import Connector, Blinker, Scene, ScenePlayer

L = 150
ENTRY_START = 25
CATA_L = L - ENTRY_START

SCENE_DARKNESS = Scene(loop=[[((0, 10, 10), L)]])  # default for bg light

# darkenss sub-frame
D = ((0, 0, 0), CATA_L)


def colorscale(base_color, frame, total_frames, target_color=(0, 0, 0)):
    """
    pulsey helper
    frame -- int num frame
    total_frames -- int pulse length
    """
    r, g, b = base_color
    rt, gt, bt = target_color
    dr, dg, db = rt - r, gt - g, bt - b

    a = min(float(frame) / total_frames, 1)  # just in case

    return (int(r + a * dr), int(g + dg * a), int(b + db * a))
    return (int(r*a), int(g*a), int(b*a))


COLOR_DARKNESS = (0, 0, 0)
COLOR_PA_1 = (200, 0, 120)  # pinkish
COLOR_PA_2 = (100, 0, 60)  # pinkish
COLOR_PB_1 = (0, 100, 200)  # greenish
COLOR_PB_2 = (0, 50, 100)  # greenish

SCENE_WALKER = Scene(
    intro=[
        [(colorscale(
            base_color=COLOR_DARKNESS,
            target_color=COLOR_PA_1,
            frame=x,
            total_frames=30), L)]
        for x in range(0, 30)
    ], loop=[
        [(colorscale(
            base_color=COLOR_PA_1,
            target_color=COLOR_PA_2,
            frame=x,
            total_frames=30), L)]
        for x in list(range(30)) + list(range(30, 0, -1))
    ] + [
        [(colorscale(
            base_color=COLOR_PA_1,
            target_color=COLOR_PB_1,
            frame=x,
            total_frames=30), L)]
        for x in list(range(30))
    ] + [
        [(colorscale(
            base_color=COLOR_PB_1,
            target_color=COLOR_PB_2,
            frame=x,
            total_frames=30), L)]
        for x in list(range(30)) + list(range(30, 0, -1))
    ] + [
        [(colorscale(
            base_color=COLOR_DARKNESS,
            target_color=COLOR_DARKNESS,
            frame=x,
            total_frames=20), L)]
        for x in list(range(20))
    ], outro=[
        [(colorscale(
            target_color=COLOR_DARKNESS,
            base_color=COLOR_PB_1,
            frame=x,
            total_frames=10), L)]
        for x in range(10, 0, -1)
    ],
)  # in room 1 and 2


class State:
    def __init__(self):
        self.player = ScenePlayer(initial_scene=SCENE_DARKNESS)
        self.state = -1

    def change_state(self, to_state):
        if to_state != self.state:
            self.state = to_state

            if to_state == 0:  # initial
                self.player.change_scene(SCENE_DARKNESS)
            else:  # primary
                self.player.change_scene(SCENE_WALKER)

    def play(self):
        return self.player.play()


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
