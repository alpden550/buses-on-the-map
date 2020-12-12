import json
import logging
import pathlib

import trio
from trio_websocket import open_websocket_url


def load_routes(path='routes'):
    filenames = pathlib.Path(path).glob('*.json')
    for filename in filenames:
        with open(filename, encoding='utf8') as file:
            yield json.load(file)


async def run_bus(ws, bus, coordinates):
    while True:
        for coordinate in coordinates:
            message = json.dumps({
                "busId": f'{bus}-0',
                "lat": coordinate[0],
                "lng": coordinate[1],
                "route": bus,
            }, ensure_ascii=False)

            await ws.send_message(message)
            await trio.sleep(0.1)


async def client():
    buses = load_routes()
    try:
        async with open_websocket_url('ws://127.0.0.1:8080/ws') as ws:
            async with trio.open_nursery() as nursery:
                for bus in buses:
                    nursery.start_soon(run_bus, ws, bus['name'], bus['coordinates'])
    except OSError as ose:
        logging.error('Connection attempt failed: %s', ose)


def main():
    trio.run(client)


if __name__ == '__main__':
    main()
