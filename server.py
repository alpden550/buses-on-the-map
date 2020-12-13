import json
from contextlib import suppress
from dataclasses import dataclass
from functools import partial

import click
import trio
from loguru import logger
from trio_websocket import serve_websocket, ConnectionClosed, WebSocketRequest, WebSocketConnection


@dataclass
class WindowBounds:
    south_lat: float
    north_lat: float
    west_lng: float
    east_lng: float

    def update(self, bounds: dict):
        self.south_lat = bounds.get("south_lat")
        self.north_lat = bounds.get("north_lat")
        self.west_lng = bounds.get("west_lng")
        self.east_lng = bounds.get("east_lng")

    def is_bus_inside(self, bus: str):
        bus_dict = json.loads(bus)
        return (
                (self.south_lat < bus_dict['lat'] < self.north_lat) and (
                self.west_lng < bus_dict['lng'] < self.east_lng)
        )


buses = []
browser = WindowBounds(0, 0, 0, 0)


async def fetch_buses(request: WebSocketRequest):
    ws = await request.accept()

    while True:
        try:
            message = await ws.get_message()
            buses.append(message)
        except ConnectionClosed:
            break


def make_bus_message() -> dict:
    response_message = {
        "msgType": "Buses",
        "buses": []
    }
    for bus in buses:
        if browser.is_bus_inside(bus):
            response_message['buses'].append(json.loads(bus))
    return response_message


async def talk_to_browser(ws: WebSocketConnection):
    while True:
        try:
            message = make_bus_message()
            await ws.send_message(json.dumps(message))
        except ConnectionClosed:
            break

        await trio.sleep(1)


async def listen_browser(ws: WebSocketConnection):
    while True:
        try:
            message = await ws.get_message()
            new_boundaries = json.loads(message).get('data')
            browser.update(new_boundaries)
        except ConnectionClosed as error:
            logger.error(f'Connection was closed: {error.reason.name}')
            break

        await trio.sleep(1)


async def handle_browser(request: WebSocketRequest):
    ws = await request.accept()

    async with trio.open_nursery() as nursery:
        nursery.start_soon(talk_to_browser, ws)
        nursery.start_soon(listen_browser, ws)


async def start_server(server: str, bus_port: int, browser_port: int):
    bus_reader = partial(serve_websocket, fetch_buses, server, bus_port, ssl_context=None)
    bus_writer = partial(serve_websocket, handle_browser, server, browser_port, ssl_context=None)
    async with trio.open_nursery() as nursery:
        nursery.start_soon(bus_reader)
        nursery.start_soon(bus_writer)


@click.command()
@click.option('--server', '-s', default='127.0.0.1', help='Server address.', type=str, show_default=True)
@click.option('--bus_port', '-b', default=8080, help='Port to receive buses data.', type=int, show_default=True)
@click.option(
    '--browser_port', '-b', default=8000, help='Port to communicate with browser.', type=int, show_default=True
)
def main(server: str, bus_port: int, browser_port: int):
    with suppress(KeyboardInterrupt):
        trio.run(start_server, server, bus_port, browser_port)


if __name__ == '__main__':
    main()
