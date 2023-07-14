import time
from enum import Enum
from flask_bootstrap import Bootstrap5
from flask import Flask, request, render_template, url_for, redirect

from sound import soundcheck
from world import World, Room

app = Flask(__name__)
Bootstrap5(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True  # serve bootstrap res locally


class State(Enum):
    "!!same states should be used in fw"

    DEBUG = 999
    INITIAL = 0
    PRIMARY = 1
    HIGH = 2


class Role(Enum):
    ROOM_UNKNOWN = 999
    ROOM_ENTRY = 0
    ROOM_LAB = 1
    ROOM_WALKER = 2
    ROOM_BEAST = 3
    ROOM_TREE = 4
    DEVICE_WALL = 5
    DEVICE_COLUMN = 6


def room_by_role(role):
    return {
        Role.ROOM_ENTRY: Room.ENTRY,
        Role.ROOM_LAB: Room.CATACOMBS,
        Role.ROOM_WALKER: Room.WALKER,
        Role.ROOM_BEAST: Room.SWAMP,
        Role.DEVICE_COLUMN: Room.COLUMN,
        Role.ROOM_TREE: Room.TREE
    }.get(role)


class Event(Enum):
    "all the events possible in the system"
    DEBUG = 999  # all to debug
    RESET = 0  # all to initial
    OP_NEXT = 1  # operator clicks "next"
    # TODO: add more


# map of default roles
# TODO: read/save, maybe?
DEFAULT_ROLES = {
    '24d7eb15b9b0': Role.ROOM_TREE,
    'a0b76556b22c': Role.ROOM_WALKER,
    '807d3ab7dae8': Role.ROOM_ENTRY,
    '9c9c1fc9b20c': Role.DEVICE_COLUMN,
    '9c9c1fcadc44': Role.ROOM_BEAST,
    '240ac4ef4434': Role.ROOM_LAB
}


class Nodes:
    """
    :node_states: -- map of existing node_id to state
    :node_roles: -- map of node_id to role
    """
    def __init__(self):
        self.node_states = {}
        self.node_roles = {}
        self.node_seen = {}

    def register(self, did):
        "returns role that this device got"
        role = DEFAULT_ROLES.get(did, Role.ROOM_UNKNOWN)
        self.node_roles[did] = role
        self.node_states[did] = State.INITIAL  # everything starts at initial
        self.node_seen[did] = time.time()

        return self.node_roles[did]

    def read_state(self, did):
        "return current state for did and note it's time"
        self.node_seen[did] = time.time()
        room = room_by_role(self.node_roles[did])
        if room:
            return WORLD.get_device_state(room)
        else:
            # FIXME: legacy fallback
            return self.node_states.get(did, State.DEBUG).value


nodes = Nodes()
WORLD = World()


@app.route('/event', methods=['POST'])
def event():
    did = request.args.get('did')
    eid = request.args.get('eid')
    if not did or not eid:
        return 'no did or eid', 400

    nodes.handle_event(Event(int(eid)), did)  # FIXME: check for eids?
    WORLD.handle_event(eid)

    return '', 200  # TODO: maybe something useful?


@app.route('/hello')
def register():
    # FIXME: add secret!
    did = request.args.get('did')
    if not did:
        return 'no did', 400

    role = nodes.register(did)
    return str(role.value)


@app.route('/state')
def state():
    # FIXME: add secret!
    did = request.args.get('did')
    if not did:
        return 'no did', 400
    return str(nodes.read_state(did))


@app.route('/ping')
def ping():
    return 'pong'


@app.route('/')
def index():
    "home page for ui control"
    events = WORLD.get_operator_events()

    return render_template(
        'index.html',
        nodes=nodes,
        desc=WORLD.get_description(),
        events=events,
        now=time.time()
    )


@app.route('/btn_action/<action>', methods=['POST'])
def btn_action(action):
    WORLD.handle_event(action)

    return redirect(url_for('index'))


if __name__ == '__main__':
    soundcheck()
    app.run(host='0.0.0.0')
