from machine import I2C, Pin, PWM
from mpu9250 import MPU9250
from time import sleep
from math import pi, cos, sin, sqrt, atan

pins = [
    Pin(i, Pin.OUT)
    for i in range(8)
]

pwms = [
    PWM(pin)
    for pin in pins
]

for pwm in pwms:
    pwm.freq(4096)

i2c = I2C(scl=Pin(17), sda=Pin(16), id=0)
sensor = MPU9250(i2c)

MAX_INT = 65025
THRESHOLD = 0.3

while True:
    
    # sensor.acceleration is all we need for this hat
    gx, gy, gz = sensor.gyro
    
    for i, pwm in enumerate(pwms):
        motor_angle = (i + 4) / 8.0 * pi * 2.0
        mx, my = cos(motor_angle), sin(motor_angle)
        
        similarity = -gy * mx + gx * my
        
        if similarity > THRESHOLD:
            
            similarity -= THRESHOLD
            similarity = sqrt(similarity)
            similarity = 0.5 + 0.5 * similarity
            
            duty_amt = int(similarity * MAX_INT)
            
            pwm.duty_u16(duty_amt)
        
        else:
            pwm.duty_u16(0)

    # delay until next observation
    sleep(1.0 / 60.0)

