import requests
import pytest
import uuid
import time


@pytest.fixture
def hub():
    """
        just the api root
    """
    return 'http://hub:5000/'


def test_foo():
    # just to test the testing
    assert True


def test_api_smoke(hub):
    '''
    checks api up to 10 secs for it to become available
    '''
    for _ in range(10):
        time.sleep(1)
        try:
            if requests.get(f'{hub}/ping').status_code == 200:
                break
        except:
            pass
    else:
        assert False


def test_flow_smoke(hub):
    did = str(uuid.uuid4())[:5]

    hello = requests.get(f'{hub}/hello?did={did}')
    assert hello.text == '999'  # role unknown

    state = requests.get(f'{hub}/state?did={did}')
    assert state.status_code == 200
    assert state.text == '0'  # state initial

    event = requests.post(f'{hub}/event?did={did}&eid=999')  # post debug
    assert event.status_code == 200

    state_2 = requests.get(f'{hub}/state?did={did}')
    assert state_2.status_code == 200
    assert state_2.text == '999'  # state debug
