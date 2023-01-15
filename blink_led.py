from machine import Pin, PWM
from time import sleep

button = Pin(18, Pin.IN, Pin.PULL_DOWN)
stop = Pin(19, Pin.IN, Pin.PULL_DOWN)
pwmLED = PWM(Pin(25))
pwmPIN0 = PWM(Pin(0)) 

t = 32512 # half brightness
f = 1000
pbval = 0
stage = 0
case = {
    0: 32512,
    1: 40000,
    2: 50000,
    3: 65025
}

pwmLED.freq(f)
pwmPIN0.freq(f)

while True:
    
    if button.value() and not pbval:
        stage += 1
        
        if stage > 10:
            stage = 0
        
    
    if stop.value():
        pwmLED.duty_u16(0)
        pwmPIN0.duty_u16(0)
        quit()
    
    t = case[stage]
    
    pwmLED.duty_u16(t)
    pwmPIN0.duty_u16(t)
    
    pbval = button.value()
    
    sleep(1.0 / 60.0)
    
#timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink)

