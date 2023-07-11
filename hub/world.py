"""
    World model and state machine
"""

import time
from enum import Enum
from collections import namedtuple

Room = namedtuple('Room', ['id', 'high_timeout'])
Event = namedtuple('Event', ['name', 'manual', 'code'])


class Room:
    ENTRY = Room(1, None)
    CATACOMBS = Room(2, None)
    WALKER = Room(3, 3 * 60)
    SWAMP = Room(4, None)
    TREE = Room(5, 5 * 60)
    COLUMN = Room(6, None)


class RoomState:
    DEBUG = 999
    INITIAL = 0
    PRIMARY = 1
    HIGH = 2


class Event(Enum):
    "logical events -- not device events!"
    RESET = Event('reset', True, 0)  # global reset
    ENTER_DREAM = Event('Enter dream', True, 1)  # start of the dream

    PLUG_WALL_A = Event('Plug into wall a', False, 2)
    PLUG_WALL_B = Event('Plug into wall b', False, 3)

    UNPLUG_WALL_A = Event('unplug from wall a', False, 4)
    UNPLUG_WALL_B = Event('unplug from wall b', False, 5)

    COLUMN_RISE = Event('column has risen', False, 6)
    COLUMN_LOW = Event('column was lowered', False, 7)

    START_WALKER = Event('activate walker', True, 8)  # start of the walker interaction
    WALKER_ENRAGE = Event('walker enrages', True, 9)
    START_SWAMP = Event('activate beast', True, 10)
    SWAMP_ENRAGE = Event('beast erages', True, 11)

    ENTER_TREE = Event('Enter tree zone', True, 12)  # party enters the tree zone starts interaction
    TREE_ENRAGE = Event('Panic at the tree', True, 13)
    RETURN_FROM_DREAM = Event('Wake up from dream', True, 14)  # party wakes up in the tent again


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

    def get_device_state(self, room):
        return self.room_state[room]

    def get_operator_events(self):
        return [e for e in self.room_events if e.manual] + [Event.RESET]

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

    def handle_event(self, event_name):
        try:
            event = Event[event_name]
        except Exception as e:
            print('NOT EVENT: %s / %s' % (event_name, e))
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
                } and self.aactive_room == Room.CATACOMBS:
            return self.handle_device(event)
        elif event in {Event.START_WALKER, Event.WALKER_ENRAGE} \
                and self.active_room == Room.WALKER:
            return self.handle_walker(event)
        elif event in {Event.START_SWAMP, Event.SWAMP_ENRAGE} \
                and self.active_room == Room.SWAMP:
            return self.handle_swamp(event)
        elif event in {Event.ENTER_TREE, Event.TREE_ENRAGE} \
                and self.active_room == Room.TREE:
            return self.handle_tree(event)
        elif event == Event.RETURN_FROM_DREAM \
                and self.active_room == Room.TREE:
            return self.return_from_dream()
        else:
            print('CANT HANDLE -- %s in %s' % (event, self.aactive_room))

    def enter_dream(self):
        self.active_room = Room.ENTRY
        self.room_events = [Event.START_WALKER]
        self.room_state = {
            r: RoomState.INITIAL for r in Room
        }

        self.room_state[Room.ENTRY] = RoomState.HIGH # light is in primary room
        # FIXME: PLAY_MUSIC

    def return_from_dream(self):
        self.active_room = Room.ENTRY
        self.room_events = []  # nothing can happen
        self.room_state = {
            r: RoomState.INITIAL for r in Room
        }

        self.room_state[Room.ENTRY] = RoomState.HIGH # light is in primary room
        # FIXME: PLAY_MUSIC

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
        elif event == Event.COLUMN_RISE:
            self.column_up = True
            # TODO: activate column timer

    def check_plugs(self):
        if self.wall_a_plugged and self.wall_b_plugged:
            # all plugged, elevate room state
            self.room_state[Room.CATACOMBS] = RoomState.HIGH  # FIXME: more modes for room
            # TODO: play music

    def handle_walker(self, event):
        self.active_room = Room.WALKER
        self.room_events = [Event.WALKER_ENRAGE, Event.START_SWAMP]
        self.room_state = {
            r: RoomState.INITIAL for r in Room
        }

        if event == Event.START_WALKER:
            self.room_state[Room.WALKER] = RoomState.PRIMARY
        else:
            self.room_state[Room.WALKER] = RoomState.HIGH
        # FIXME: play music

    def handle_swamp(self, event):
        self.active_room = Room.SWAMP
        self.room_events = [Event.SWAMP_ENRAGE, Event.ENTER_TREE]
        self.room_state = {
            r: RoomState.INITIAL for r in Room
        }

        if event == Event.START_SWAMP:
            self.room_state[Room.SWAMP] = RoomState.PRIMARY
        else:
            self.room_state[Room.SWAMP] = RoomState.HIGH
        # FIXME: play music

    def handle_tree(self, event):
        self.active_room = Room.TREE
        self.room_events = [Event.TREE_ENRAGE, Event.RETURN_FROM_DREAM]
        self.room_state = {
            r: RoomState.INITIAL for r in Room
        }

        if event == Event.START_TREE:
            self.room_state[self.active_room] = RoomState.PRIMARY
        else:
            self.room_state[self.active_room] = RoomState.HIGH
        # FIXME: play music
