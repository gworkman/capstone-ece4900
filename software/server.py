import asyncio
import struct
import json
import websockets
import time
from bleak import BleakClient, discover

address = "40:f5:20:70:2c:82"
DATA_CHAR_UUID = 'F477FD95-41F0-4C73-9093-5DA7DC624DF0'


async def send_data(websocket, path):
    global address
    print('searching for devices')
    devices = await discover()
    for device in devices:
        if device.name.lower() == 'bosu ballers':
            print('found device')
            print(device.address)
            address = device.address
    async with BleakClient(address) as client:
        last_time = time.time()
        current_time = time.time()
        while True:
            raw_data = await client.read_gatt_char(DATA_CHAR_UUID)
            current_time = time.time()
            print(f'elapsed time between samples: {(current_time - last_time)} s')
            last_time = current_time
            parsed_data = struct.unpack('<ffffffH', raw_data)
            data = {
                'accel_data': parsed_data[0:3],
                'gyro_data': parsed_data[3:6],
                'force_data': parsed_data[6]
            }
            await websocket.send(json.dumps(data))
    

start_server = websockets.serve(send_data, "localhost", 8888)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
