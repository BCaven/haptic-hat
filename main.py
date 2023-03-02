"""
main.py - Runs automatically when the Raspberry Pi Pico is provided power
"""

from machine import I2C, Pin, PWM

from mpu9250 import MPU9250
from ak8963 import AK8963

from time import sleep
from math import pi, cos, sin, sqrt, atan2

MODE_GYRO = 0
MODE_ACCELERATION = 1
MODE_COMPASS = 2
MODE_NOOP = 3

mode = MODE_COMPASS

RECALIBRATE = False
ak8963_offset = (-23.69063, -6.096094, -7.751953)
ak8963_scale = (1.000207, 1.014458, 0.9857479)

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

if RECALIBRATE:
    print("Starting calibration")
    ak8963 = AK8963(i2c)
    offset, scale = ak8963.calibrate(count=256, delay=200)
    print("Offset (hard iron)")
    print(offset)
    print("Scale (soft iron)")
    print(scale)

else:
    ak8963 = AK8963(
        i2c,
        offset=ak8963_offset,
        scale=ak8963_scale
    )

sensor = MPU9250(i2c, ak8963=ak8963)

MAX_INT = 65025
THRESHOLD = 0.9

def rotate2D(a, b, theta):
    ct = cos(theta)
    st = sin(theta)
    return (
        ct * a - st * b,
        st * a + ct * b
    )

def cross(v1, v2):
    a1, a2, a3 = v1
    b1, b2, b3 = v2
    return (
        a2 * b3 - a3 * b2,
        a3 * b1 - a1 * b3,
        a1 * b2 - a2 * b1
    )

def normalize(v1):
    x, y, z = v1
    inv_m = 1.0 / (x ** 2 + y ** 2 + z ** 2) ** 0.5
    return (
        x * inv_m,
        y * inv_m,
        z * inv_m
    )

def compass_mode():
    # sensor.acceleration is all we need for this hat
    gx, gy, gz = sensor.magnetic
    
    # rotate on Y axis to account for hat tilt
    theta = -pi / 6
    gx, gz = rotate2D(gx, gz, theta)
    
    # rotate on X axis to correct position on hat
    theta = -pi * 1/24
    gy, gz = rotate2D(gy, gz, theta)
    
    #ux, uy, uz = sensor.acceleration
    
    ux, uy, uz = (0, 0, 1)
    
    nx, ny, nz = cross((gx, gy, gz), (ux, uy, uz))
    nx, ny, nz = normalize((nx, ny, nz))
    
    for i, pwm in enumerate(pwms):
        # Determine motor's local position
        motor_angle = (i) / 8.0 * pi * 2.0 + pi
        
        mx, my, mz = (
            cos(motor_angle),
            sin(motor_angle),
            0
        )

        # Determine if motor is pointing towards "north"
        similarity = mx * nx + my * ny + mz * nz
        
        if similarity > THRESHOLD:
            
            # Normalize to (0, 1) range
            similarity -= THRESHOLD
            similarity *= 1.0 / (1.0 - THRESHOLD)
            
            # Activate motor
            duty_amt = int(similarity * MAX_INT)
            pwm.duty_u16(duty_amt)
        
        else:
            pwm.duty_u16(0)

def acceleration_mode():
    # sensor.acceleration is all we need for this hat
    ax, ay, az = normalize(sensor.acceleration)
    
    # rotate on Y axis to account for hat tilt
    theta = -pi / 6
    ax, az = rotate2D(ax, az, theta)
    
    # rotate on X axis to correct position on hat
    theta = -pi * 1/24
    ay, az = rotate2D(ay, az, theta)
    
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

def gyro_mode():
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

def noop_mode():
    for pwm in pwms:
        pwm.duty_u16(0)

def start_timer(callback, freq):
    period = 1.0 / freq
    while True:
        callback()
        sleep(period)

callbacks = {
    MODE_GYRO: gyro_mode,
    MODE_COMPASS: compass_mode,
    MODE_ACCELERATION: acceleration_mode,
    MODE_NOOP: noop_mode
}

start_timer(callbacks[mode], freq=60)
