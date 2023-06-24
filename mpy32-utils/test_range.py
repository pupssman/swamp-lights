"""
two blips -- starts connecting
one blip -- while connting
five blips -- faild to connect and/or register

three blips -- exception on request
one blip -- successful request
"""

import machine
import time
import urequests
import ubinascii
import _thread
import network

# FIXME: write a connector!
wlan = network.WLAN(network.STA_IF)

# unique id is 4 bytes, get nicer repr
DID = ubinascii.hexlify(machine.unique_id()).decode('utf-8')

# FIXME: read those from drive?
HOST = '192.168.0.24'
PORT = 5000
SSID = 'wood_wonders'
PWD = ''

led = machine.Pin(2, machine.Pin.OUT)
# it should be locked on gnd,


class Blinker:
    def __init__(self, led):
        self.led = led

    def _blink(self, sleep_s, number_times):
        for _ in range(number_times):
            self.led.value(1)
            time.sleep(sleep_s)
            self.led.value(0)
            time.sleep(sleep_s)

    def fast(self, times=1):
        self._blink(0.1, times)

    def slow(self, times=1):
        self._blink(0.5, times)


blink = Blinker(led)


def do_connect():
    """
    will try to connect for at most 30 secs
    will raise Exceptionif not connected
    """
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        blink.fast(2)
        wlan.connect(SSID, PWD)

        for _ in range(5):
            # 30 seconds to connect
            if not wlan.isconnected():
                time.sleep(1)
                blink.fast(1)
            else:
                break  # from for loop
        else:
            # did not break
            blink.fast(5)
            raise Exception('did not connect after 30 secs')

    print('network config:', wlan.ifconfig())


def register():
    res = urequests.get('http://%s:%s/hello?did=%s' % (HOST, PORT, DID))
    print(res.text)


def get_state():
    res = urequests.get('http://%s:%s/state?did=%s' % (HOST, PORT, DID))
    print(res.text)
    return int(res.text)


def report_event(eid):
    res = urequests.post('http://%s:%s/event?did=%s&eid=%d' %
                         (HOST, PORT, DID, eid))
    print(res.text)


class State:
    def __init__(self):
        self.loop = None
        self._last_state = None

    def change_state(self, to_state):
        """
           :returns: if there was change, for debug purposes 
        """
        # FIXME: change properly
        if self._last_state == to_state:
            return

        self._last_state = to_state
        return True

    def on_internal_problem(self):
        # FIXME: good only for dev
        self.loop = None


STATE = State()


def button_interrupt(pin_irq):
    # FIXME: god knows whats in these args
    print('button pressed: %s' % pin_irq)
    report_event(999)  # debug event


def check_for_state(delay):
    "threadfunc"
    print('check for state thread started')

    while True:
        time.sleep(delay)  # check for state each second
        try:
            new_state_code = get_state()
            if STATE.change_state(new_state_code):
                blink.fast(2)
            else:
                blink.fast(1)
        except Exception as e:
            blink.fast(5)
            print('oops: %s' % e)


if __name__ == '__main__':
    try:
        do_connect()
        register()
        blink.slow(2)
    except Exception:
        # failed to connect / register, play the dead loop
        STATE.on_internal_problem()
        blink.slow(5)

    _thread.start_new_thread(check_for_state, (1,))

    while True:
        time.sleep(1)  # busyloop