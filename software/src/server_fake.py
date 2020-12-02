import asyncio
import websockets
import json
import random

async def hello(websocket, path):

    while True:
        print('sending data')
        data = {'data': [int(val) for val in random.randbytes(7)]}
        await websocket.send(json.dumps(data))
        await asyncio.sleep(0.1)

start_server = websockets.serve(hello, "localhost", 8888)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()