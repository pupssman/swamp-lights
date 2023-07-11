import time
from common import Connector, ButtonTracker, Relay, State, Blinker

STATE = State()

R_A = Relay(18, initial=False)
R_B = Relay(19, initial=False)


BTN_A = ButtonTracker(
   pin=13,
   on_high=lambda: R_B.on(),
   on_low=lambda: R_B.off())

BTN_B = ButtonTracker(
   pin=4,
   on_high=lambda: R_A.on(),
   on_low=lambda: R_A.off())

if __name__ == '__main__':
    print('Beginning buttons')
    blink = Blinker()

    def on_state_callback(sid):
        print('Got new state %s' % sid)

    connector = Connector(blink, on_state=on_state_callback)
    connector.begin()

    print('Now main in sleeping')

    while True:
        time.sleep(1)  # busyloop
