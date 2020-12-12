import json
import logging
import pathlib
import random

import trio
from trio_websocket import open_websocket_url


def load_routes(path='routes'):
    filenames = pathlib.Path(path).glob('*.json')
    for filename in filenames:
        with open(filename, encoding='utf8') as file:
            yield json.load(file)


def generate_bus_id(route_id, bus_index):
    return f"{route_id}-{bus_index}"


async def run_bus(ws, bus_id, bus, coordinates):
    offset = random.randint(0, len(coordinates))
    for coordinate in coordinates[offset:]:
        message = json.dumps({
            "busId": bus_id,
            "lat": coordinate[0],
            "lng": coordinate[1],
            "route": bus,
        }, ensure_ascii=False)

        await ws.send_message(message)
        await trio.sleep(0.3)


async def client():
    routes = load_routes()
    try:
        async with open_websocket_url('ws://127.0.0.1:8080/ws') as ws:
            async with trio.open_nursery() as nursery:
                for route in routes:
                    for index, _ in enumerate(range(5)):
                        bus_id = generate_bus_id(route['name'], index)
                        nursery.start_soon(run_bus, ws, bus_id, route['name'], route['coordinates'])
    except OSError as ose:
        logging.error('Connection attempt failed: %s', ose)


def main():
    trio.run(client)


if __name__ == '__main__':
    main()
