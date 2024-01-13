from machine import I2C, Pin, PWM
import gc
from mpu9250 import MPU9250
from time import sleep
from math import pi, cos, sin, sqrt, atan

start_button, calibrate_button = (
    Pin(18, Pin.IN, Pin.PULL_DOWN),
    Pin(19, Pin.IN, Pin.PULL_DOWN)
)

pins = [
    Pin(i, Pin.OUT)
    for i in range(8)
]

pwms = [
    PWM(pin)
    for pin in pins
]

for pwm in pwms:
    pwm.freq(2048)

i2c = I2C(scl=Pin(17), sda=Pin(16), id=0)
sensor = MPU9250(i2c)

# sensor.acceleration
# sensor.gyro
# sensor.magnetic
# sensor.temperature

def normalize_vector(v):
    x, y, z = v
    invMag = 1.0 / sqrt(x * x + y * y + z * z)
    return x * invMag, y * invMag, z * invMag

MAX_INT = 65025

while True:
    
    # sensor.acceleration is all we need for this hat
    ax, ay, az = normalize_vector(sensor.acceleration)
    
    # rotate on Y axis to account for hat tilt
    theta = -pi / 6
    ax, az = (
        cos(theta) * ax - sin(theta) * az,
        cos(theta) * az + sin(theta) * ax
    )
    
    # rotate on X axis to correct position on hat
    theta = -pi * 1/24
    ay, az = (
        cos(theta) * ay - sin(theta) * az,
        cos(theta) * az + sin(theta) * ay
    )
    
    for i, pwm in enumerate(pwms):
        # relative motor positions
        # the +4 came from trial and error
        motor_angle = (i + 4) / 8.0 * pi * 2.0
        mx, my = cos(motor_angle), sin(motor_angle)
        
        # similarity value (dot product)
        similarity = ax * mx + ay * my
        
        # threshold for buzzing
        if similarity > 0.25:
            
            # scale value for better
            # motor strengths
            similarity = sqrt(similarity)
            similarity = 0.5 + similarity * 0.5
            
            # convert to unsigned 16-bit integer
            amt = int(similarity * MAX_INT)
            pwm.duty_u16(amt)
        
        else:
            
            # stop motor if similarity is
            # below the threshold
            pwm.duty_u16(0)

    # delay until next observation
    sleep(1.0 / 10)
    gc.collect()
