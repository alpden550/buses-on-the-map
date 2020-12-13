import json

import pytest

from validators import validate_bus


@pytest.fixture
def message():
    msg = {"busId": "92-0", "lat": 55.903616977703, "lng": 37.543359808968, "route": "92"}
    yield msg


def test_dict_is_not_json(message):
    result = validate_bus(message)
    assert result
    assert 'errors' in result
    assert result['errors'][0] == 'Requires valid JSON'


def test_bus_keys(message):
    del message['route']
    result = validate_bus(json.dumps(message))
    assert result
    assert 'errors' in result
    assert result['errors'][0] == 'Requires all fields for bus.'


def test_busid_exists(message):
    del message['busId']
    message['bus_id'] = 'busId'
    result = validate_bus(json.dumps(message))
    assert result
    assert 'errors' in result
    assert result['errors'][0] == 'Requires busId specified.'


def test_lat_exists(message):
    del message['lat']
    message['lat_1'] = 0
    result = validate_bus(json.dumps(message))
    assert result
    assert 'errors' in result
    assert result['errors'][0] == 'Requires coordinates specified.'


def test_lng_exists(message):
    del message['lng']
    message['lng_1'] = 0
    result = validate_bus(json.dumps(message))
    assert result
    assert 'errors' in result
    assert result['errors'][0] == 'Requires coordinates specified.'


def test_parse_coordinates(message):
    message['lat'] = 'string'
    message['lng'] = 'string'
    result = validate_bus(json.dumps(message))
    assert result
    assert 'errors' in result
    assert result['errors'][0] == "Can't parse coordinate in float."
