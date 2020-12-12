import json
from contextlib import suppress
from functools import partial

import trio
from loguru import logger
from trio_websocket import serve_websocket, ConnectionClosed, WebSocketRequest, WebSocketConnection

buses = []


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
        response_message['buses'].append(json.loads(bus))
    return response_message


async def talk_to_browser(ws: WebSocketConnection):
    while True:
        try:
            message = make_bus_message()
            await ws.send_message(json.dumps(message))
            await trio.sleep(0.1)
        except ConnectionClosed:
            break


async def listen_browser(ws: WebSocketConnection):
    while True:
        try:
            message = await ws.get_message()
            logger.debug(message)
        except ConnectionClosed as error:
            logger.error(f'Connection was closed: {error.__context__}')


async def handle_browser(request: WebSocketRequest):
    ws = await request.accept()

    async with trio.open_nursery() as nursery:
        nursery.start_soon(talk_to_browser, ws)
        nursery.start_soon(listen_browser, ws)


async def server():
    bus_reader = partial(serve_websocket, fetch_buses, '127.0.0.1', 8080, ssl_context=None)
    bus_writer = partial(serve_websocket, handle_browser, '127.0.0.1', 8000, ssl_context=None)
    async with trio.open_nursery() as nursery:
        nursery.start_soon(bus_reader)
        nursery.start_soon(bus_writer)


def main():
    with suppress(KeyboardInterrupt):
        trio.run(server)


if __name__ == '__main__':
    main()
