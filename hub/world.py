"""
    World model and state machine
"""

import time
from enum import Enum
from collections import namedtuple

from sound import PLAYER

RoomC = namedtuple('Room', ['id', 'high_timeout'])
EventC = namedtuple('Event', ['name', 'manual', 'code'])


class Room(Enum):
    ENTRY = RoomC(1, None)
    CATACOMBS = RoomC(2, None)
    WALKER = RoomC(3, 3 * 60)
    SWAMP = RoomC(4, None)
    TREE = RoomC(5, 5 * 60)
    COLUMN = RoomC(6, None)


class RoomState:
    DEBUG = 999
    INITIAL = 0  # aka standby, nothing happens here. typically darkness
    PRIMARY = 1  # aka active room
    HIGH = 2  # aka enrage / etc
    EXTRA = 3  # for room entry as high of catacombs because they share light


class Event(Enum):
    "logical events -- not device events!"
    RESET = EventC('reset', True, 0)  # global reset
    ENTER_DREAM = EventC('Enter dream', True, 1)  # start of the dream

    PLUG_WALL_A = EventC('Plug into wall a', False, 2)
    PLUG_WALL_B = EventC('Plug into wall b', False, 3)

    UNPLUG_WALL_A = EventC('unplug from wall a', False, 4)
    UNPLUG_WALL_B = EventC('unplug from wall b', False, 5)

    COLUMN_RISE = EventC('column has risen', False, 6)
    COLUMN_LOW = EventC('column was lowered', False, 7)
    COLUMN_EXPLODE = EventC('column has exploded', True, 15)
    CATACOMBS_COLLAPSE = EventC('column has exploded', True, 16)
    CATACOMBS_ENTER = EventC('column has exploded', True, 17)

    START_WALKER = EventC('activate walker', True, 8)  # start of the walker interaction
    WALKER_ENRAGE = EventC('walker enrages', True, 9)
    START_SWAMP = EventC('activate beast', True, 10)
    SWAMP_ENRAGE = EventC('beast erages', True, 11)

    ENTER_TREE = EventC('Enter tree zone', True, 12)  # party enters the tree zone starts interaction
    TREE_ENRAGE = EventC('Panic at the tree', True, 13)
    RETURN_FROM_DREAM = EventC('Wake up from dream', True, 14)  # party wakes up in the tent again


EVENTS_BY_ID = {
    e.value.code: e
    for e in Event
}

EVENTS_BY_NAME = {
    e.name: e
    for e in Event
}


class World:
    '''
    :field room_events: -- list of not ignored events (aka plug/unplug, etc)
        >>> World().handle_event('RESET')
        'ololo'
    '''
    def __init__(self):
        self.reset()

    def reset(self):
        self.active_room = Room.ENTRY
        self.room_events = [Event.ENTER_DREAM]
        self.change_time = time.time()

        # particular tracked stuff
        self.column_up = False
        self.wall_a_plugged = False
        self.wall_b_plugged = False

        self.room_state = {
            r: RoomState.INITIAL for r in Room
        }
        self.room_state[Room.ENTRY] = RoomState.PRIMARY  # in reset we wait for new party
        PLAYER.set_room_track(1, 0)  # cosy sounds

    def get_device_state(self, room):
        return self.room_state[room]

    def get_operator_events(self):
        return [e for e in self.room_events if e.value.manual] + [Event.RESET]

    def get_description(self):
        result = '''
            Active: %s
            Possbile events: %s
            Column: %s
            wall_a: %s
            wall_b: %s
        ''' % (self.active_room, self.room_events, self.column_up,
               self.wall_a_plugged, self.wall_b_plugged)
        return result

    def handle_event(self, event_name_or_id):
        print('Before event: %s' % self.get_description())
        if event_name_or_id in EVENTS_BY_NAME:
            event = Event[event_name_or_id]
        elif event_name_or_id in EVENTS_BY_ID:
            event = EVENTS_BY_ID[event_name_or_id]
        else:
            print('NOT EVENT: %s ' % (event_name_or_id,))
            return

        self.change_time = time.time()

        if event == Event.RESET:
            return self.reset()
        # can only enter dream if active is entry room
        elif event == Event.ENTER_DREAM and self.active_room == Room.ENTRY:
            return self.enter_dream()
        # devices work in catacombs
        elif event in {
            Event.COLUMN_LOW,  Event.COLUMN_RISE,
            Event.PLUG_WALL_A, Event.PLUG_WALL_B,
            Event.UNPLUG_WALL_A, Event.UNPLUG_WALL_B
        }:
            return self.handle_device(event)
        elif event in {Event.START_WALKER, Event.WALKER_ENRAGE}:
            return self.handle_walker(event)
        elif event in {Event.START_SWAMP, Event.SWAMP_ENRAGE}:
            return self.handle_swamp(event)
        elif event in {Event.ENTER_TREE, Event.TREE_ENRAGE}:
            return self.handle_tree(event)
        elif event == Event.COLUMN_EXPLODE:
            return self.handle_column_explode()
        elif event == Event.CATACOMBS_ENTER:
            return self.handle_enter_catacombs()
        elif event == Event.CATACOMBS_COLLAPSE:
            return self.handle_catacomb_collapse()
        elif event == Event.RETURN_FROM_DREAM \
                and self.active_room == Room.TREE:
            return self.return_from_dream()
        else:
            print('CANT HANDLE -- %s in %s' % (event, self.active_room))
        print('After event: %s' % self.get_description())

    def handle_column_explode(self):
        self.room_state[Room.COLUMN] = RoomState.HIGH  # just so it is obvious
        # TODO: sound?

    def handle_catacomb_collapse(self):
        PLAYER.set_room_track(2, 1)  # cosy sounds

    def handle_enter_catacombs(self):
        PLAYER.set_room_track(2, 0)  # cosy sounds

    def enter_dream(self):
        self.active_room = Room.ENTRY
        self.room_events = [Event.START_WALKER, Event.COLUMN_EXPLODE,
                            Event.CATACOMBS_COLLAPSE, Event.CATACOMBS_ENTER]
        self.room_state = {
            r: RoomState.INITIAL for r in Room
        }

        self.room_state[Room.ENTRY] = RoomState.HIGH  # light is in primary room
        self.room_state[Room.COLUMN] = RoomState.PRIMARY  # actiavet column
        PLAYER.set_room_track(1, 1)  # psycho sounds

    def return_from_dream(self):
        self.active_room = Room.ENTRY
        self.room_events = []  # nothing can happen
        self.room_state = {
            r: RoomState.INITIAL for r in Room
        }

        self.room_state[Room.ENTRY] = RoomState.PRIMARY  # light is in primary room
        PLAYER.set_room_track(1, 0)  # cosy sounds

    def handle_device_event(self, event):
        if event == Event.PLUG_WALL_A:
            self.wall_a_plugged = True
            self.check_plugs()
        elif event == Event.UNPLUG_WALL_A:
            self.wall_a_plugged = False
            self.check_plugs()
        elif event == Event.PLUG_WALL_B:
            self.wall_b_plugged = True
            self.check_plugs()
        elif event == Event.UNPLUG_WALL_B:
            self.wall_b_plugged = False
            self.check_plugs()
        elif event == Event.COLUMN_LOW:
            self.column_up = False
            # TODO: disable column
            # self.room_state[Room.COLUMN] = RoomState.INITIAL
        elif event == Event.COLUMN_RISE:
            self.column_up = True
            # self.room_state[Room.COLUMN] = RoomState.PRIMARY
            # TODO: activate column timer

    def check_plugs(self):
        if self.wall_a_plugged and self.wall_b_plugged:
            # all plugged, elevate room state
            self.room_state[Room.ENTRY] = RoomState.EXTRA
            # TODO: play music
            PLAYER.set_room_track(2, 1)  # cosy collapse
        else:
            self.room_state[Room.ENTRY] = RoomState.EXTRA
            # TODO: play music
            PLAYER.set_room_track(2, 0)  # cosy sounds

    def handle_walker(self, event):
        self.active_room = Room.WALKER
        self.room_events = [Event.WALKER_ENRAGE, Event.START_SWAMP]
        self.room_state = {
            r: RoomState.INITIAL for r in Room
        }

        if event == Event.START_WALKER:
            PLAYER.set_room_track(3, 0)  # initial sounds
            self.room_state[Room.WALKER] = RoomState.PRIMARY
        else:
            PLAYER.set_room_track(3, 1)  # danger sounds
            self.room_state[Room.WALKER] = RoomState.HIGH

    def handle_swamp(self, event):
        self.active_room = Room.SWAMP
        self.room_events = [Event.SWAMP_ENRAGE, Event.ENTER_TREE]
        self.room_state = {
            r: RoomState.INITIAL for r in Room
        }

        if event == Event.START_SWAMP:
            PLAYER.set_room_track(4, 0)  # initial sounds
            self.room_state[Room.SWAMP] = RoomState.PRIMARY
        else:
            # no elevated music here -- just speedup
            self.room_state[Room.SWAMP] = RoomState.HIGH

    def handle_tree(self, event):
        self.active_room = Room.TREE
        self.room_events = [Event.TREE_ENRAGE, Event.RETURN_FROM_DREAM]
        self.room_state = {
            r: RoomState.INITIAL for r in Room
        }

        if event == Event.ENTER_TREE:
            PLAYER.set_room_track(5, 0)  # initial sounds
            self.room_state[self.active_room] = RoomState.PRIMARY
        else:
            PLAYER.set_room_track(5, 1)  # initial sounds
            self.room_state[self.active_room] = RoomState.HIGH
