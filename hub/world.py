"""
    World model and state machine 
"""

import time
from enum import Enum
from collections import namedtuple

Room = namedtuple('Room', ['id', 'high_timeout'])
Event = namedtuple('Event', ['name', 'manual'])

class Rooms:
    ENTRY = Room(1, None)
    CATACOMBS = Room(2, None)
    WALKER = Room(3, 3 * 60)
    SWAMP = Room(4, None)
    TREE = Room(5, 5 * 60)


class Event(Enum):
    "logical events -- not device events!"
    RESET = Event('reset', True)  # global reset
    ENTER_DREAM = Event('Enter dream', True)  # start of the dream
    
    PLUG_WALL_A = Event('Plug into wall a', False)
    PLUG_WALL_B = Event('Plug into wall b', False)

    UNPLUG_WALL_A = Event('unplug from wall a', False)
    UNPLUG_WALL_B = Event('unplug from wall b', False)

    COLUMN_RISE = Event('column has risen', False)
    COLUMN_LOW = Event('column was lowered', False)

    START_WALKER = Event('activate walker', True)  # start of the walker interaction
    WALKER_ENRAGE = Event('walker enrages', True)
    START_SWAMP = Event('activate beast', True)
    SWAMP_ENRAGE = Event('beast erages', True)

    ENTER_TREE = Event('Enter tree zone', True)  # party enters the tree zone starts interaction
    TREE_ENRAGE = Event('Panic at the tree', True)
    RETURN_FROM_DREAM = Event('Wake up from dream', True)  # party wakes up in the tent again


class World:
    '''
    :field room_events: -- list of not ignored events (aka plug/unplug, etc)
        >>> World().handle_event('RESET')
        'ololo'
    '''
    def __init__(self):
        self.reset()

    def reset(self):
        self.active_room = Rooms.ENTRY
        self.room_events = [Event.ENTER_DREAM]
        self.change_time = time.time()

        # particular tracked stuff
        self.column_up = False
        self.wall_a_plugged = False
        self.wall_b_plugged = False

    def get_device_state(self, room):
        pass

    def get_operator_events(self):
        pass

    def get_description(self):
        pass

    def handle_event(self, event_name):
        try:
            event = Event[event_name]
        except Exception as e:
            print('NOT EVENT: %s' % event_name)
            return

        if event == Event.RESET:
            return 'ololo'

        # TODO: handle more events)