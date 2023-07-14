from common import Connector, Blinker, Scene, ScenePlayer

L = 150
ENTRY_START = 25
CATA_L = L - ENTRY_START

SCENE_DARKNESS = Scene(loop=[[((0, 0, 0), L)]])  # just black

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


COLOR_COZY = (250, 70, 0)
COLOR_DARKNESS = (0, 0, 0)

SCENE_COZY = Scene(
    intro=[
        [(colorscale(
            base_color=COLOR_DARKNESS,
            target_color=COLOR_COZY,
            frame=x,
            total_frames=10), ENTRY_START), D]
        for x in range(0, 10)
    ], loop=[
        [(colorscale(COLOR_COZY, frame=x, total_frames=30), ENTRY_START), D]
        for x in list(range(30)) + list(range(30, 0, -1))
    ], outro=[
        [(colorscale(
            target_color=COLOR_DARKNESS,
            base_color=COLOR_COZY,
            frame=x,
            total_frames=30), ENTRY_START), D]
        for x in range(30, 0, -1)
    ] + [[(COLOR_DARKNESS, L)] for _ in range(50)],
)  # in room 1 and 2

COLOR_PA = (200, 0, 120)  # pinkish
COLOR_PB = (0, 100, 200)  # greenish

SCENE_PSYCHO = Scene(
    intro=[
        [(colorscale(
            base_color=COLOR_DARKNESS,
            target_color=COLOR_PA,
            frame=x,
            total_frames=30), L)]
        for x in range(0, 30)
    ], loop=[
        [(colorscale(
            base_color=COLOR_PA,
            target_color=COLOR_PB,
            frame=x,
            total_frames=150), L)]
        for x in list(range(150)) + list(range(150, 0, -1))
    ], outro=[
        [(colorscale(
            target_color=COLOR_PA,
            base_color=COLOR_COZY,
            frame=x,
            total_frames=10), L)]
        for x in range(10, 0, -1)
    ],
)  # in room 1 and 2

SCENE_WALKER = Scene()  # in room 3
SCENE_TREE = Scene()  # in room 4


class State:
    def __init__(self):
        self.player = ScenePlayer(initial_scene=SCENE_DARKNESS)
        self.state = -1

    def change_state(self, to_state):
        if to_state != self.state:
            self.state = to_state

            if to_state == 0:  # initial
                self.player.change_scene(SCENE_DARKNESS)
            elif to_state == 1:  # primary
                self.player.change_scene(SCENE_COZY)
            elif to_state == 2:  # scene high
                self.player.change_scene(SCENE_PSYCHO)
            else:
                self.player.change_scene(SCENE_PSYCHO)

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
