from machine import I2C, Pin, PWM
from micropython import const
import gc
from sys import exit
from time import sleep

MAX_INT = const(65025)

pins = [
    Pin(i, Pin.OUT)
    for i in range(8)
]

pwms = [
    PWM(pin)
    for pin in pins
]

toggle_pwm = Pin(18, Pin.IN, Pin.PULL_DOWN)
next_pwm = Pin(19, Pin.IN, Pin.PULL_DOWN)

toggle_pwm_debounce = 0
next_pwm_debounce = 0
current_pwm = 0

for pwm in pwms:
    pwm.freq(4096)

duties = [
    0 for _ in pins
]

while True:
    try:
        for i, pwm in enumerate(pwms):
            pwm.duty_u16(duties[i])

    except KeyboardInterrupt:
        for pwm in pwms:
            pwm.duty_u16(-1)
        
        gc.collect()
        exit()