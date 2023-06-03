from enum import Enum
from flask_bootstrap import Bootstrap
from flask import Flask, request, render_template

app = Flask(__name__)
Bootstrap(app)


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


class Event(Enum):
    "all the events possible in the system"
    DEBUG = 999  # all to debug
    RESET = 0  # all to initial
    # TODO: add more


# map of default roles
# TODO: read/save, maybe?
DEFAULT_ROLES = {
    'foo': Role.ROOM_ENTRY,
    'bar': Role.DEVICE_WALL
}


class World:
    """
    :node_states: -- map of existing node_id to state
    :node_roles: -- map of node_id to role
    """
    def __init__(self):
        self.node_states = {}
        self.node_roles = {}

    def register(self, did):
        "returns role that this device got"
        role = DEFAULT_ROLES.get(did, Role.ROOM_UNKNOWN)
        self.node_roles[did] = role
        self.node_states[did] = State.INITIAL  # everything starts at initial

        return self.node_roles[did]

    def read_state(self, did):
        "return current state for did"
        return self.node_states.get(did, State.DEBUG)

    def handle_event(self, eid, did=None):
        """
            handle event based on when and why
            :eid: -- enum for Event
        """
        if eid == Event.DEBUG:
            for node in self.node_states:
                self.node_states[node] = State.DEBUG
        elif eid == Event.RESET:
            for node in self.node_states:
                self.node_states[node] = State.INITIAL
        else:
            raise ValueError('Unknown event')


world = World()


@app.route('/event', methods=['POST'])
def event():
    did = request.args.get('did')
    eid = request.args.get('eid')
    if not did or not eid:
        return 'no did or eid', 400

    world.handle_event(Event(int(eid)), did)  # FIXME: check for eids?

    return '', 200  # TODO: maybe something useful?


@app.route('/hello')
def register():
    # FIXME: add secret!
    did = request.args.get('did')
    if not did:
        return 'no did', 400

    role = world.register(did)
    return str(role.value)


@app.route('/state')
def state():
    # FIXME: add secret!
    did = request.args.get('did')
    if not did:
        return 'no did', 400
    return str(world.read_state(did).value)


@app.route('/ping')
def ping():
    return 'pong'


@app.route('/')
def index():
    "home page for ui control"
    return render_template('index.html', world=world)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
