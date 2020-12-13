import json


def validate_browser(msg: str) -> dict:
    result = {"errors": [], "msgType": "Errors"}
    try:
        message = json.loads(msg)
    except (json.JSONDecodeError, TypeError):
        result['errors'].append('Requires valid JSON')
        return result

    if not list(message.keys()) == ['msgType', 'data'] or not message['msgType'] == 'newBounds':
        result['errors'].append('Requires msgType and data')
        return result

    if not list(message['data'].keys()) == ['south_lat', 'north_lat', 'west_lng', 'east_lng']:
        result['errors'].append('Requires south_lat, north_lat, west_lng, east_lng in the coordinates.')
        return result

    try:
        [float(coordinate) for coordinate in message['data'].values()]
    except ValueError:
        result['errors'].append("Can't parse coordinate in float.")
        return result


def validate_bus(msg: str) -> dict:
    result = {"errors": [], "msgType": "Errors"}
    try:
        message = json.loads(msg)
    except (json.JSONDecodeError, TypeError):
        result['errors'].append('Requires valid JSON')
        return result

    if not len(message.keys()) == 4:
        result['errors'].append('Requires all fields for bus.')
        return result

    if 'busId' not in message:
        result['errors'].append('Requires busId specified.')
        return result

    if 'lat' not in message or 'lng' not in message:
        result['errors'].append('Requires coordinates specified.')
        return result

    try:
        _, _ = float(message['lat']), float(message['lng'])
    except ValueError:
        result['errors'].append("Can't parse coordinate in float.")
        return result
