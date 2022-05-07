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
kit.motor1.throttle = 0.9
kit.motor2.throttle = 0.9

time.sleep(3) #seconds

kit.motor1.throttle = 0
kit.motor2.throttle = 0
