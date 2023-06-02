import requests
import pytest


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
    assert requests.get(f'{hub}/ping').status_code == 200
