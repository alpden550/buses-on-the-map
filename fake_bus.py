import json
import pathlib
import random
from contextlib import suppress
from itertools import cycle

import trio
from trio_websocket import open_websocket_url


def load_routes(path='routes'):
    filenames = pathlib.Path(path).glob('*.json')
    for filename in filenames:
        with open(filename, encoding='utf8') as file:
            yield json.load(file)


def generate_bus_id(route_id, bus_index):
    return f"{route_id}-{bus_index}"


async def run_bus(send_channel, bus_id, bus, coordinates):
    offset = random.randint(0, len(coordinates))

    for coordinate in coordinates[offset:]:
        message = json.dumps({
            "busId": bus_id,
            "lat": coordinate[0],
            "lng": coordinate[1],
            "route": bus,
        }, ensure_ascii=False)
        await send_channel.send(message)
        await trio.sleep(0.3)


async def send_updates(receive_channel):
    async with open_websocket_url('ws://127.0.0.1:8080/ws') as ws:
        async for message in receive_channel:
            await ws.send_message(message)


async def client():
    routes = load_routes()

    async with trio.open_nursery() as nursery:
        send_channels = []
        for _ in range(4):
            send_channel, receive_channel = trio.open_memory_channel(0)
            send_channels.append(send_channel)
            nursery.start_soon(send_updates, receive_channel)
        channel_choices = cycle(send_channels)

        for route in routes:
            for index in range(5):
                bus_id = generate_bus_id(route['name'], index)
                sender = next(channel_choices)
                nursery.start_soon(run_bus, sender, bus_id, route['name'], route['coordinates'])


def main():
    with suppress(KeyboardInterrupt):
        trio.run(client)


if __name__ == '__main__':
    main()
