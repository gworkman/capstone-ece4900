# main.py

# imports
import time
import struct
import ubluetooth as bluetooth
from micropython import const
from ble_advertising import advertising_payload
from uos import urandom

# constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)

# functions


def bt_irq(event, data):
    if event == _IRQ_CENTRAL_CONNECT:
        # A central has connected to this peripheral.
        conn_handle, addr_type, addr = data
        connections.add(conn_handle)
        ble.gap_advertise(None)
        print('[bluetooth] device connected')
    elif event == _IRQ_CENTRAL_DISCONNECT:
        # A central has disconnected from this peripheral.
        conn_handle, addr_type, addr = data
        connections.remove(conn_handle)
        ble.gap_advertise(500000)
        print('[bluetooth] device disconnected')
    else:
        print('[bluetooth] received event {}'.format(event))


# entrypoint
ble = bluetooth.BLE()
ble.active(True)
ble.irq(bt_irq)
ble.config(gap_name='Bosu')

# configure the services that will be advertised
ACCEL_UUID = bluetooth.UUID('7ED5A5BC-8013-4753-B199-0A364D52E5DE')
ACCEL_CHAR = (bluetooth.UUID('F477FD95-41F0-4C73-9093-5DA7DC624DF0'),
              bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)
ACCEL_SERVICE = (ACCEL_UUID, (ACCEL_CHAR,),)
SERVICES = (ACCEL_SERVICE,)

((accel,),) = ble.gatts_register_services(SERVICES)

connections = set()

# this advertising payload can't be too long
payload = advertising_payload(name='Bosu Ballers')
ble.gap_advertise(500000, adv_data=payload)

while True:
    for conn in connections:
        # generate random values for testing
        xyz = urandom(3)
        x = ((xyz[0] / 256.0) - 0.5) * 10.0
        y = ((xyz[1] / 256.0) - 0.5) * 10.0
        z = ((xyz[2] / 256.0) - 0.5) * 10.0
        ble.gatts_write(accel, struct.pack('<fff', x, y, z))
        ble.gatts_notify(conn, accel)
    time.sleep_ms(100)
