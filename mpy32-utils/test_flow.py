import machine
import time
import neopixel as nx
import urequests
import ubinascii
import _thread

# unique id is 4 bytes, get nicer repr
DID = ubinascii.hexlify(machine.unique_id()).decode('utf-8')

# FIXME: read those from drive?
HOST = '192.168.0.2'
PORT = 5000
SSID = ''
PWD = ''

# LED strip configuration
# number of pixels
num_pixels = 300
# strip control gpio
strip_pin = 2
button_pin = 5  # dp 5 to read button
np = nx.NeoPixel(machine.Pin(strip_pin), num_pixels)
led = machine.Pin(2, machine.Pin.OUT)
# it should be locked on gnd,
button = machine.Pin(button_pin, machine.Pin.IN, machine.Pin.PULL_UP)


def light_full(color):
    for n in range(num_pixels):
        np[n] = color
    # np.fill(color)
    np.write()


# FIXME: somehow colors are messed, names should be correct
G = [(n * 4, 0, 0) for n in range(32)]
R = [(0, n * 4, 0) for n in range(32)]
B = [(0, 0, n * 4) for n in range(32)]
K = [(0, 0, 0)] * 3

RED_LOOP = K + R + R[::-1] + K
BLUE_LOOP = K + B + B[::-1] + K
GREEN_LOOP = K + G + G[::-1] + K


def play_loop(loop):
    for c in loop:
        light_full(c)
        time.sleep(.05)


def do_connect():
    """
    will try to connect for at most 30 secs
    will raise Exceptionif not connected
    """
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(SSID, PWD)

        for _ in range(30):
            # 30 seconds to connect
            if not wlan.isconnected():
                time.sleep(1)
            else:
                break  # from for loop
        else:
            # did not break
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
        self.loop = GREEN_LOOP

    def change_state(self, to_state):
        # FIXME: change properly
        if to_state == 999:
            self.loop = BLUE_LOOP
        else:
            self.loop = GREEN_LOOP

    def on_internal_problem(self):
        # FIXME: good only for dev
        self.loop = RED_LOOP


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
            STATE.change_state(new_state_code)
        except Exception as e:
            print('oops: %s' % e)


if __name__ == '__main__':
    # 3 is like machine.Pin.IRQ_RISING but for both (rising / falling)
    button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_interrupt)

    try:
        do_connect()
        register()
    except Exception:
        # failed to connect / register, play the dead loop
        STATE.on_internal_problem()

    _thread.start_new_thread(check_for_state, (1,))

    while True:
        play_loop(STATE.loop)
