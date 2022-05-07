from signal import signal, SIGTERM, SIGHUP, pause
from time import sleep
from threading import Thread
from gpiozero import DistanceSensor

import time
import board
from adafruit_motorkit import MotorKit

#Simple code pulled from motorkit doc to move motor back and forth.

#Must activate I2C before this will work
# https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c

kit = MotorKit(i2c=board.I2C())

#The four motor spots on the Pi hat are available as motor1 , motor2 , motor3 , and
# motor4 .

#Foward

reading = True
sensor = DistanceSensor(echo=20, trigger=21)

def safe_exit(signum, frame):
    exit(1)

def read_distance():
    global message
    kit.motor1.throttle = 0.8
    kit.motor2.throttle = 0.8

    while reading:
        message = f"Distance: {sensor.value:1.2f} m"
        print(message)
        if (sensor.value < 0.8):
            kit.motor1.throttle = 0.0
            kit.motor2.throttle = 0.0
            sleep(3)
            #Backup logic
            kit.motor1.throttle = -0.8
            kit.motor2.throttle = -0.8
            sleep(2)
            kit.motor1.throttle = 0.9
            kit.motor2.throttle = 0.0
            sleep(2)
        else:
            kit.motor1.throttle = 0.5
            kit.motor2.throttle = 0.5
        sleep(1)
        

try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    reader = Thread(target=read_distance, daemon=True)
    reader.start()

    pause()

except KeyboardInterrupt:
    kit.motor1.throttle = 0.0
    kit.motor2.throttle = 0.0
    pass

finally:
    reading = False
    reader.join()
    sensor.close()
