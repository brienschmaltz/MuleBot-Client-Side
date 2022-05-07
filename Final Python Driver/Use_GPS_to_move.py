#Developed by Brien Schmaltz, Thien Nguyen
#Client side code for raspberry pi robot.
# Link to this scripts github: https://github.com/brienschmaltz/MuleBot-Client-Side
# Link to mobile application the bot communicates with: https://github.com/brienschmaltz/Team-Projects-Mulebot-MobileApplication

#GPS imports

import time
import board
import busio

import adafruit_gps
import serial

#GPS specific libraries for comparing lat,long

from geographiclib.geodesic import Geodesic
from geopy import distance

#Imports for Magnetometer 

import math
import adafruit_lis2mdl


#Imports for Motor

from adafruit_motorkit import MotorKit

#Imports for Screen 

import I2C_LCD_driver

#Regex
import re

#SOCKET IMPORTS
from socket import *
from time import sleep

#Magnetometer Setup MUST USE the calibration script in the Magnetometer folder to get this value. 
hardiron_calibration =[[-80.55, -16.349999999999998], [-29.849999999999998, 19.65], [-45.3, -29.7]]

def main():
    
    #Setup all pi accesories
    

    #Motor Setup
    kit = MotorKit(i2c=board.I2C())
    
    #Screen Setup
    display = I2C_LCD_driver.lcd()

    
    #Magnetometer Setup
    i2c = board.I2C()  # uses board.SCL and board.SDA
    sensor = adafruit_lis2mdl.LIS2MDL(i2c)

    
    #GPS Setup

    uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=10)

    gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial

    # Turn on the basic GGA and RMC info (what you typically want)
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

    # Set update rate to once a second (1hz) which is what you typically want.
    gps.send_command(b"PMTK220,1000")
    # Or decrease to once every two seconds by doubling the millisecond value.
    # Be sure to also increase your UART timeout above!
    # gps.send_command(b'PMTK220,2000')
    # You can also speed up the rate, but don't go too fast or else you can lose
    # data during parsing.  This would be twice a second (2hz, 500ms delay):
    # gps.send_command(b'PMTK220,500')
    
    #Socket Setup
    
    HOST = "192.168.42.1" #
    PORT = 8080 #open port 8080 for connection
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1) #how many connections can it receive at one time
    conn, addr = s.accept() #accept the connection
    print("Connected by: " , addr) #print the address of the person connected
    
    #------------------------------------------------

    #START HERE

    #------------------------------------------------

    
    output_not_following = "Not Following"
    output_following = "Following"
    output_intializing = "Preparing for takeoff"
    output_getting_gps = "Waiting for"
    output_getting_gps2 = "GPS signal"


    #Fancy scrolling text for bot intialization
    padding = " " * 16
    padded_string = output_intializing + padding

    for i in range (0, len(output_intializing)):
        lcd_text = output_intializing[i:(i+16)]
        display.lcd_display_string(lcd_text,1)
        sleep(0.4)
        display.lcd_display_string(padding,1)

    sleep(1)
    display.lcd_clear()

    try:
            while True:
                
                #Get the LAT LONG from the mobile application
                #Uses Python sockets
                
                data = conn.recv(1024) #how many bytes of data will the server receive
                incoming_string = repr(data)
                print("\nInitial Data Received: ", incoming_string[7:], "\n")
                
                #Just parse start of data. Has a bunch of crap
                to_parse = incoming_string[10:]
                
                #See function above
                to_parse = remove_after_character(to_parse)
                print("After character parse", to_parse, "\n")
                
                #String to Float string should look like this: "Lat: 34.123456 Long: 120.2431325"
                matches = re.findall("[+-]?\d+.\d+", to_parse)

                
                #Convert to floats
                float_lat = float(matches[0])
                float_long = float(matches[1])
                
                print("Current user position:", str(float_lat) , "Long:", str(float_long), "\n")
                print("----------------------------")
                #Set user position
                user_position = (float_lat, float_long)
                
                #sleep(3)

                # Make sure to call gps.update() every loop iteration and at least twice
                # as fast as data comes from the GPS unit (usually every second).
                # This returns a bool that's true if it parsed new data (you can ignore it
                # though if you don't care and instead look at the has_fix property).
                gps.update()
                
                if not gps.has_fix:
                    # Try again if we don't have a fix yet.
                    print("Waiting for fix...")
                    
                    #Print message to lcd screen
                    display.lcd_display_string(output_getting_gps,1)
                    display.lcd_display_string(output_getting_gps2,2)
                    
                    continue
                    
                # We have a fix! (gps.has_fix is true)
                
                #The money
                lat = gps.latitude
                longitude = gps.longitude
                
                current_bot_position = (lat, longitude)
                current_distance = distance.distance(user_position, current_bot_position)
                print("Current Distance:", current_distance)
                print("\nCurrent Bot Lat:" , lat , "Long: ", longitude)
               
                #angle (in degrees) between the mulebot and the users position
                bearing = Geodesic.WGS84.Inverse(current_bot_position[0],current_bot_position[1],user_position[0],user_position[1])

                
                #Calculate final bearing based off of azil. Not needed. Azil used for around the globe caluclations in flights.
                heading_needed = bearing['azi1']
                #Adjust for true north
                heading_needed+=6.39
                if(heading_needed < 0):
                    heading_needed+=360
                    
                print("\nCurrent Heading to user:" , heading_needed)

                #get Magnetometer readings
                magvals = sensor.magnetic
                normvals = normalize(magvals)

                # we will only use X and Y for the compass calculations, so hold it level!
                bot_heading = int(math.atan2(normvals[1], normvals[0]) * 180.0 / math.pi)
                # compass_heading is between -180 and +180 since atan2 returns -pi to +pi
                # this translates it to be between 0 and 360
                bot_heading+= 180
                print("\nCurrent Bot Heading: ", bot_heading)

                #At this point, all variables are gathered, main logic can proceed.
                
                #Never implemented
                #Distance check before any movement. Slow down the bot and wait
                #if(current_distance < 0.005):
                #    kit.motor1.throttle = 0.5
                #    kit.motor2.throttle = 0.5
                #    time.sleep(2)
                #    print("Code got to Distance Check")
                #else:
                    #Pass will continue onward. Bot is not close enough to the user.
                    #continue
                    
                       
                #Start motor forward
                kit.motor1.throttle = 0.9
                kit.motor2.throttle = 0.9
                    
                heading_difference = bot_heading - heading_difference
                print("\nHeading Difference:" , heading_difference )
                #time.sleep(3)

                                    
                #0 degrees is north
                #90 is west (This is weird, not sure, west/east seem flipped.)
                #180 is south
                #270 is east
                
                
                #Motor 2 is the motor not parallel with the gps antenna. So if facing ultrasonic sensor, one on the right.
                #Motor 1 makes bot turn left, or west
                #Motor 2 makes bot turn right, or 
                
                
                #We need to get the right heading first. 
                #heading_needed = 355 
                #bot_heading = 5. 
                # We want -10
                

                if(heading_needed > bot_heading):
                
                    #true for 355
                    #-(5) - (360 - 355)
                    # -5 - 5 = -10
                    heading_difference = -(botheading) - (360 - heading_needed)

                else: 
                      
                      heading_difference = 360-heading_needed + bot_heading
                      

                   #If difference  is greater than 180 need to make an adjustment
                    abs(heading_difference)

                if(heading_difference > 10):
                    #Bot is not heading in the user's general direction
                
                    if(11 <= heading_difference >= 179):
                                
                        #Turn bot west 
                              
                        kit.motor1.throttle = 0.9
                        kit.motor2.throttle = 0.0
                        
                        #kit.motor1.throttle = 0.0
                        #kit.motor1.throttle = 0.0


                    if(180 <= heading_difference >= 360):
                         
                          #Turn bot east
                        
                          #kit.motor1.throttle = 0.0
                          #kit.motor2.throttle = 0.0
                        
                          kit.motor1.throttle = 0.0
                          kit.motor2.throttle = 0.9
                else:
                    #heading in right direction
                    #kit.motor1.throttle = 0.0
                    #kit.motor2.throttle = 0.0
                    kit.motor1.throttle = 0.9
                    kit.motor2.throttle = 0.9
                    sleep(2)
                    
                print("\n-----------------\n")

                #output_distance = "Distance:" + str(current_distance)
                rounded_heading_needed = round(heading_needed, 2)
                output_heading_needed = "Usr_Dir: " + str(rounded_heading_needed)
                output_bot_heading = "Bot_Dir: " + str(bot_heading)
                
                
                display.lcd_display_string(output_heading_needed,1)
                display.lcd_display_string(output_bot_heading,2)


                    
    except KeyboardInterrupt:
        # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
        print("Cleaning up!")
        
        #Motor
        kit.motor1.throttle = 0.0
        kit.motor2.throttle = 0.0
        
        #Screen
        display.lcd_clear()
        
        #Socket
        conn.close()
        print("Connection with " , addr, " is now over.")
                
#This function removes any "excess" data sent from the socket. Sometimes it will spam like so
#data received: "Lat: 39.7591403 Long: -84.0751361\x00!Lat: 39.7591403 Long: -84.0751361". This gets rid of everything after
#"\x00" which is considered a "!" in python
def remove_after_character(incoming_data):
    #Seperator
    sep = "\\"
    
    #Bool
    where_exclamation = sep in incoming_data
    
    if(where_exclamation == False):
        #nothing was found
        return incoming_data
    else:
        #make that string work
        stripped = incoming_data.split(sep, 1)[0]
        return stripped
    
    
# This will take the magnetometer values, adjust them with the calibrations
# and return a new array with the XYZ values ranging from -100 to 100
def normalize(_magvals):

    ret = [0, 0, 0]
    for i, axis in enumerate(_magvals):
        minv, maxv = hardiron_calibration[i]
        axis = min(max(minv, axis), maxv)  # keep within min/max calibration
        ret[i] = (axis - minv) * 200 / (maxv - minv) + -100
    return ret


if __name__ == "__main__":
    main()