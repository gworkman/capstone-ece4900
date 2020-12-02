import asyncio
from bleak import BleakClient

address = "40:f5:20:70:2c:82"
ACCEL_CHAR_UUID = 'F477FD95-41F0-4C73-9093-5DA7DC624DF0'


async def send_data(reader, writer):
    async with BleakClient(address) as client:
        while True:
            accel_data = await client.read_gatt_char(ACCEL_CHAR_UUID)
            writer.write(accel_data)
            await writer.drain()


async def main(address):
    server = await asyncio.start_server(send_data, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    async with server:
        await server.serve_forever()

asyncio.run(main(address))
