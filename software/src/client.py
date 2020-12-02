import asyncio
import struct

async def main():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    while True:
        data = await reader.read(12)
        if len(data) == 12:
            print(f"Received: {struct.unpack('<fff', data)}")

    print('Close the connection')
    writer.close()

asyncio.run(main())