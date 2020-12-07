# main.py

# imports
import time
import struct
import ubluetooth as bluetooth
import machine
import esp32
from machine import I2C, Pin, ADC
from imu import MPU6050
from micropython import const
from ble_advertising import advertising_payload

# constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
THIRTY_SECONDS = const(30000)

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

# interrupt function

def pin_sleep(p):
    print("Going to sleep (pin press).")
    # Reconfigure pin as wakeup pin
    esp32.wake_on_ext0(pin = wakeSleepPin, level = esp32.WAKEUP_ANY_HIGH)
    # Wait half a second for button debounce
    time.sleep_ms(500)
    machine.deepsleep()

# entrypoint
i2c = I2C(0)
imu = MPU6050(i2c)
ble = bluetooth.BLE()
adc = ADC(Pin(34))
ble.active(True)
ble.irq(bt_irq)
ble.config(gap_name='Bosu Ballers')
print([hex(item) for item in ble.config('mac')])

# configure the services that will be advertised
DATA_UUID = bluetooth.UUID('7ED5A5BC-8013-4753-B199-0A364D52E5DE')
DATA_CHAR = (bluetooth.UUID('F477FD95-41F0-4C73-9093-5DA7DC624DF0'),
              bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY)
DATA_SERVICE = (DATA_UUID, (DATA_CHAR,),)

SERVICES = (DATA_SERVICE,)
((data_srv,),) = ble.gatts_register_services(SERVICES)

connections = set()

# this advertising payload can't be too long
payload = advertising_payload(name='Bosu Ballers')
ble.gap_advertise(50000, adv_data=payload)

#wake/sleep pin
wakeSleepPin = Pin(12, Pin.IN, Pin.PULL_DOWN)

# Set up GPIO pin to put to sleep
wakeSleepPin.irq(trigger = Pin.IRQ_FALLING, handler = pin_sleep)

# Boolean for checking bluetooth connection
hasConnection = False

deadline = time.ticks_add(time.ticks_ms(), THIRTY_SECONDS)

while True:
    #Run if there is a connection, then recheck to see if connection was dropped. If dropped, set timer before deepsleep
    if hasConnection:
        hasConnection = conn in connections
        if not hasConnection:
            ble.gap_advertise(50000, adv_data=payload)
            deadline = time.ticks_add(time.ticks_ms(),THIRTY_SECONDS)
    for conn in connections:
        hasConnection = True
        accel_xyz = imu.accel.xyz
        gyro_xyz = imu.gyro.xyz
        force_val = adc.read()
        accel_buf = struct.pack('<fff', *accel_xyz)
        gyro_buf = struct.pack('<fff', *gyro_xyz)
        force_buf = struct.pack('<H', force_val)
        buf = accel_buf + gyro_buf + force_buf
        ble.gatts_write(data_srv, buf)
        ble.gatts_notify(conn, data_srv)
    time.sleep_ms(250)
    if not hasConnection and time.ticks_diff(deadline,time.ticks_ms()) <= 0:
        print("Going to sleep")
        # Reconfigure pin as wakeup pin
        esp32.wake_on_ext0(pin = wakeSleepPin, level = esp32.WAKEUP_ANY_HIGH)
        # Wait half a second for button debounce
        time.sleep_ms(500)
        machine.deepsleep()
