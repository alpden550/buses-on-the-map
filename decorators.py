from functools import wraps
from typing import Callable

import trio
from loguru import logger
from trio_websocket import HandshakeError, ConnectionClosed


def relaunch_on_disconnect(delay: int = 1) -> Callable:
    def decorator(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            while True:
                try:
                    await func(*args, **kwargs)
                except HandshakeError as error:
                    logger.error(f'Connection error: {error.__context__}')
                    await trio.sleep(delay)
                except ConnectionClosed as error:
                    logger.error(f'Connection was closed: {error.__context__}')
                    await trio.sleep(delay)
        return inner

    return decorator
