# main.py
import time
from machine import Pin, PWM

i = 0
adj = 1

green = PWM(Pin(18))
green.freq(100)
green.duty(0)

while True:
    green.duty(i)
    i += adj
    if i >= 100:
        adj = -1
    elif i <= 0:
        adj = 1

    time.sleep_ms(50)
