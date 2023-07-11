"""
two blips -- starts connecting
one blip -- while connting
five blips -- faild to connect and/or register

three blips -- exception on request
one blip -- successful request
"""
from common import Connector, Blinker


if __name__ == '__main__':
    print('Beginning debug for connection')
    blink = Blinker()

    def on_state_callback(sid):
        print('Got new state %s' % sid)
    connector = Connector(blink, on_state=on_state_callback)
    connector.begin()

    print('Now main in sleeping')

    while True:
        time.sleep(1)  # busyloop
