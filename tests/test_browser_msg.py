import json

import pytest
from validators import validate_browser


@pytest.fixture
def message():
    message = {
        "msgType": "newBounds",
        "data": {
            "south_lat": 55.73764553509855,
            "north_lat": 55.78444072745938,
            "west_lng": 37.599763870239265,
            "east_lng": 37.75666236877442
        }
    }
    yield message


def test_dict_is_not_json(message):
    result = validate_browser(message)
    assert result
    assert 'errors' in result
    assert result['errors'][0] == 'Requires valid JSON'


def test_invalid_json():
    message = '"msgType": "newBounds", "data": {}}'
    result = validate_browser(message)
    assert result
    assert 'errors' in result
    assert result['errors'][0] == 'Requires valid JSON'


def test_invalid_msg_type(message):
    message['msgType'] = 'new'
    result = validate_browser(json.dumps(message))
    assert result
    assert 'errors' in result
    assert result['errors'][0] == 'Requires msgType and data'


def test_invalid_msg_keys(message):
    message['new'] = 'data'
    result = validate_browser(json.dumps(message))
    assert result
    assert 'errors' in result
    assert result['errors'][0] == 'Requires msgType and data'


def test_invalid_coordinates_names(message):
    message['data'] = {'none': 0, 'north_lat': 0, 'west_lng': 0, 'east_lng': 0}
    result = validate_browser(json.dumps(message))
    assert result
    assert 'errors' in result
    assert result['errors'][0] == 'Requires south_lat, north_lat, west_lng, east_lng in the coordinates.'


def test_invalid_coordinates_values(message):
    message['data']['north_lat'] = 'string'
    result = validate_browser(json.dumps(message))
    assert result
    assert 'errors' in result
    assert result['errors'][0] == "Can't parse coordinate in float."
