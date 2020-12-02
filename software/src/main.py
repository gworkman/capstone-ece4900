# main.py

# imports
import time
import struct
import ubluetooth as bluetooth
import machine
import esp32
from machine import I2C
from machine import Pin
from imu import MPU6050
from micropython import const
from ble_advertising import advertising_payload

# constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
THIRTY_SECONDS = const(30000)
TEN_SECONDS = const(10000)

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
adc = machine.ADC(Pin(34))
ble.active(True)
ble.irq(bt_irq)
ble.config(gap_name='Bosu')
print('hello world')

# configure the services that will be advertised
ACCEL_UUID = bluetooth.UUID('7ED5A5BC-8013-4753-B199-0A364D52E5DE')
ACCEL_CHAR = (bluetooth.UUID('F477FD95-41F0-4C73-9093-5DA7DC624DF0'),
              bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)
ACCEL_SERVICE = (ACCEL_UUID, (ACCEL_CHAR,),)

GYRO_UUID = bluetooth.UUID('a29c1085-11cb-4643-8ddc-19883e67afeb')
GYRO_CHAR = (bluetooth.UUID('495d7e2c-a9b1-42ab-ab3a-af75dcefca06'),
              bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)
GYRO_SERVICE = (GYRO_UUID, (GYRO_CHAR,),)

FORCE_UUID = bluetooth.UUID('e55a7bcb-e58e-4582-a439-adfc2f0b14b9')
FORCE_CHAR = (bluetooth.UUID('fed668b3-5471-4797-a2e5-c0e4760b7321'),
              bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)
FORCE_SERVICE = (FORCE_UUID, (FORCE_CHAR,),)

SERVICES = (ACCEL_SERVICE,GYRO_SERVICE,FORCE_SERVICE,)
((accel,),(gyro,),(force,),) = ble.gatts_register_services(SERVICES)

connections = set()

# this advertising payload can't be too long
payload = advertising_payload(name='Bosu Ballers')
ble.gap_advertise(500000, adv_data=payload)

#wake/sleep pin
wakeSleepPin = Pin(14, Pin.IN, Pin.PULL_DOWN)

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
            deadline = time.ticks_add(time.ticks_ms(),TEN_SECONDS)
    for conn in connections:
        hasConnection = True
        accel_xyz = imu.accel.xyz
        gyro_xyz = imu.gyro.xyz
        force = adc.read()
        ble.gatts_write(accel, struct.pack('<fff', *accel_xyz))
        ble.gatts_write(gyro, struct.pack('<fff', *gyro_xyz))
        ble.gatts_write(force, struct.pack('<H', force))
        ble.gatts_notify(conn, accel)
        ble.gatts_notify(conn, gyro)
        ble.gatts_notify(conn, force)
    time.sleep_ms(250)
    if not hasConnection and time.ticks_diff(deadline,time.ticks_ms()) <= 0:
        print("Going to sleep")
        # Reconfigure pin as wakeup pin
        esp32.wake_on_ext0(pin = wakeSleepPin, level = esp32.WAKEUP_ANY_HIGH)
        # Wait half a second for button debounce
        time.sleep_ms(500)
        machine.deepsleep()
