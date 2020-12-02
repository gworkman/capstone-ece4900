import asyncio
import struct
import json
import websockets
from bleak import BleakClient, discover

address = "40:f5:20:70:2c:82"
ACCEL_CHAR_UUID = 'F477FD95-41F0-4C73-9093-5DA7DC624DF0'
GYRO_CHAR_UUID = '495d7e2c-a9b1-42ab-ab3a-af75dcefca06'
FORCE_CHAR_UUID = 'fed668b3-5471-4797-a2e5-c0e4760b7321'


async def send_data(websocket, path):
    global address
    devices = await discover()
    for device in devices:
        if device.name.lower() == 'bosu ballers':
            print(device.name)
            print(device.address)
            address = device.address
    async with BleakClient(address) as client:
        while True:
            accel_data = await client.read_gatt_char(ACCEL_CHAR_UUID)
            gyro_data = await client.read_gatt_char(GYRO_CHAR_UUID)
            force_data = await client.read_gatt_char(FORCE_CHAR_UUID)
            data = {
                'accel_data': struct.unpack('<fff', accel_data),
                'gyro_data': struct.unpack('<fff', gyro_data),
                'force_data': struct.unpack('<H', force_data)[0]
            }
            await websocket.send(json.dumps(data))
    

start_server = websockets.serve(send_data, "localhost", 8888)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
