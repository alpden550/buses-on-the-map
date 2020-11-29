import trio
from trio_websocket import serve_websocket, ConnectionClosed


async def server(request):
    ws = await request.accept()
    while True:
        try:
            message = await ws.get_message()
            await ws.send_message(message)
        except ConnectionClosed:
            break


async def main():
    await serve_websocket(server, '127.0.0.1', 8000, ssl_context=None)


if __name__ == '__main__':
    trio.run(main)
