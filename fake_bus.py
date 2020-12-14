import json
import pathlib
import random
from contextlib import suppress
from itertools import cycle

import click
import trio
from loguru import logger
from trio_websocket import open_websocket_url

from decorators import relaunch_on_disconnect


def load_routes(path: str = 'routes', routes_number: int = None):
    if routes_number:
        logger.info(f'Will be loaded only {routes_number} first routes from routes.')
    filenames = pathlib.Path(path).glob('*.json')
    for index, filename in enumerate(filenames, start=1):
        if routes_number and index >= routes_number:
            break
        with open(filename, encoding='utf8') as file:
            yield json.load(file)


def generate_bus_id(route_id: str, bus_index: int, emulator_id: int = None):
    return f"{route_id}-{bus_index}-{emulator_id}" if emulator_id else f"{route_id}-{bus_index}"


async def run_bus(send_channel: trio.MemorySendChannel, bus_id: str, bus: str, coordinates: list):
    offset = random.randint(0, len(coordinates))

    for coordinate in coordinates[offset:]:
        message = json.dumps({
            "busId": bus_id,
            "lat": coordinate[0],
            "lng": coordinate[1],
            "route": bus,
        }, ensure_ascii=False)
        await send_channel.send(message)


@relaunch_on_disconnect()
async def send_updates(server: str, receive_channel: trio.MemoryReceiveChannel):
    async with open_websocket_url(server) as ws:
        async for message in receive_channel:
            await ws.send_message(message)


async def client(
        server: str,
        routes_number: int,
        buses_per_route: int,
        websockets_number: int,
        emulator_id: int,
        refresh_timeout: int
):
    routes = load_routes(routes_number=routes_number)

    async with trio.open_nursery() as nursery:
        send_channels = []
        for _ in range(websockets_number):
            send_channel, receive_channel = trio.open_memory_channel(0)
            send_channels.append(send_channel)
            nursery.start_soon(send_updates, server, receive_channel)
        channel_choices = cycle(send_channels)

        for route in routes:
            for index in range(buses_per_route):
                bus_id = generate_bus_id(route['name'], index, emulator_id)
                sender = next(channel_choices)
                nursery.start_soon(run_bus, sender, bus_id, route['name'], route['coordinates'])


@click.command()
@click.option('--server', '-s', default='ws://0.0.0.0:8080/ws', help='Server address.', type=str, show_default=True)
@click.option('--routes_number', '-r', help='Routes amount.', type=int)
@click.option('--buses_per_route', '-b', default=3, help='Buses on an one route.', type=int, show_default=True)
@click.option('--websockets_number', '-w', default=5, help='Amount of opened websockets.', type=int, show_default=True)
@click.option('--emulator_id', '-e', help='Prefix for bus id.', type=int)
@click.option('--refresh_timeout', '-t', help='Timeout for updating server coordinates', type=int, show_default=True)
def main(
        server: str,
        routes_number: int,
        buses_per_route: int,
        websockets_number: int,
        emulator_id: int,
        refresh_timeout: int
):
    with suppress(KeyboardInterrupt):
        trio.run(
            client, server, routes_number, buses_per_route, websockets_number, emulator_id, refresh_timeout
        )


if __name__ == '__main__':
    main()
