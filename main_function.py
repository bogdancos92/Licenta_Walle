import os
import RPi.GPIO as GPIO
from time import sleep
import time
import distance
import traffic_recognition
import numpy as np
import cv2
import sys

#setting left engine pins
LEFT_POZ 	= 6
LEFT_NEG 	= 13
PWM_LEFT 	= 12

#setting right engine pins
RIGHT_POZ 	= 20
RIGHT_NEG 	= 21
PWM_RIGHT 	= 26

#set GPIO Pins for front ultrasonic sensor
GPIO_TRIGGER_FRONT  = 17
GPIO_ECHO_FRONT     = 18

#set GPIO Pins for side ultrasonic sensor
GPIO_TRIGGER_SIDE   = 22
GPIO_ECHO_SIDE      = 23

#PWM factor
PWM = 0
PWM_FOR_TURNING = 0
PWM_FOR_STRAIGHT = 0

#surface coefficient
surface_coef = 1.0

#distance from sign
distance_from_sign = 30 #cm

TRAFFIC_SIGNS = [
        'Turn Right', # turnRight
        'Turn Left', # turnLeft
        'Move Straight', # moveStraight
        'Turn Back', # turnBack
    ]

#setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#left motor setup
GPIO.setup(LEFT_POZ,GPIO.OUT)
GPIO.setup(LEFT_NEG,GPIO.OUT)
GPIO.setup(PWM_LEFT,GPIO.OUT)

#right motor setup
GPIO.setup(RIGHT_POZ,GPIO.OUT)
GPIO.setup(RIGHT_NEG,GPIO.OUT)
GPIO.setup(PWM_RIGHT,GPIO.OUT)

#ultrasonic setup
GPIO.setup(GPIO_TRIGGER_FRONT, GPIO.OUT)
GPIO.setup(GPIO_ECHO_FRONT, GPIO.IN)
GPIO.setup(GPIO_TRIGGER_SIDE, GPIO.OUT)
GPIO.setup(GPIO_ECHO_SIDE, GPIO.IN)

#frequency setup
p1 = GPIO.PWM(PWM_LEFT,500)
p2 = GPIO.PWM(PWM_RIGHT,500)
p1.start(PWM)
p2.start(PWM)

#let the setup settle
sleep(2)

# define range HSV for blue color of the traffic sign
lower_blue = np.array([85,100,70])
upper_blue = np.array([115,255,255])

camera = cv2.VideoCapture(0)

def set_PWM(value):
    global PWM
    PWM = value
    p1.ChangeDutyCycle(PWM)
    p2.ChangeDutyCycle(PWM)
    sleep(0.1)

#interpolation function
def map(x, in_min, in_max, out_min, out_max):
    value = 0.0
    value = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    return value

#compute RPM based on PWM
def compute_RPM():
    #3V...125RPM
    #5V...200RPM
    #6V...230RPM
    voltage = map(PWM, 0, 100, 0.0, 6.0)
    RPM = 0
    if voltage < 3.0:
        voltage = 3.0
        RPM = 125
    elif voltage >= 3.0 and voltage < 5:
        RPM = map (voltage, 3.0, 5.0 , 125, 200)
    elif voltage >=5.0 and voltage < 6.0:
        RPM = map (voltage, 5.0, 6.0 , 200, 230)
    elif voltage >= 6.0:
        voltage = 6.0
        RPM = 230
    print('RPM = ' + str(RPM) + ' for PWM = ' + str(PWM) + ' and voltage = ' + str(voltage))
    return RPM

#compute time needed to spin 90 degrees
def compute_timer():
    RPM = compute_RPM()
    # distance to move 130mm
    # one rotation = pi * 65mm = 204
    # 0.637 rotations   ... x sec
    # RPM rotations     ... 60 sec
    # x = 0.637 * 60 sec / RPM
    time = ((0.637 * 60.0)/RPM) * surface_coef
    print ('Time to spin' + str(time))
    return time

def average_distance():
    average = distance.compute(GPIO_TRIGGER_FRONT, GPIO_ECHO_FRONT)
    average += distance.compute(GPIO_TRIGGER_FRONT, GPIO_ECHO_FRONT)
    average /= 2
    return average

#main function for motor control
def set_motor(A1,A2,B1,B2):
    GPIO.output(LEFT_POZ,A1)
    GPIO.output(LEFT_NEG,A2)
    GPIO.output(RIGHT_POZ,B1)
    GPIO.output(RIGHT_NEG,B2)
        
#direction control functions
def stop():
    set_motor(0,0,0,0)
    set_PWM(0)
    print("Stop")

def forward():
    set_motor(1,0,0,1)
    set_PWM(PWM_FOR_STRAIGHT)
    print("Straight")

def reverse():
    set_motor(0,1,1,0)
    set_PWM(PWM_FOR_STRAIGHT)

def right(timer):
    set_motor(1,0,1,0)
    set_PWM(PWM_FOR_TURNING)
    print("Turning right")
    sleep(timer)
    stop()

def left(timer):
    set_motor(0,1,0,1)
    set_PWM(PWM_FOR_TURNING)
    print("Turning left")
    sleep(timer)
    stop()


#kind of a main function
def main():
    global surface_coef
    global PWM_FOR_TURNING
    global PWM_FOR_STRAIGHT

    print('Ok get ready')
    
    if len(sys.argv) is 5:
        if sys.argv[1] == 'go':
            surface_coef = float(sys.argv[2])
            PWM_FOR_TURNING = int(sys.argv[3])
            PWM_FOR_STRAIGHT = int(sys.argv[4])

            try:

                while True:
                    sleep(1)
                    #Start car
                    forward()
                    
                    #calculate distance from sign
                    remaining_distance = average_distance()
                    
                    #while distance is less than the desired distance, keep going
                    while remaining_distance > distance_from_sign:
                        remaining_distance = distance.compute(GPIO_TRIGGER_FRONT, GPIO_ECHO_FRONT)
                        if remaining_distance < distance_from_sign:
                            stop()
                            sleep(1)
                            break

                    text = 'None'

                    while True:
                        text = traffic_recognition.findTrafficSign(camera, lower_blue, upper_blue)
                        message = '..................................'
                        if text in TRAFFIC_SIGNS:

                            #Traffic sign found
                            message = 'Found sign ' + text

                            #compute time to spin
                            set_PWM(PWM_FOR_TURNING)
                            timer = compute_timer()
                            set_PWM(0)

                            #choose direction to follow
                            if text == 'Turn Right':
                                right(timer)
                                print("Car should have turned right by now")
                                break
                            elif text == 'Turn Left':
                                left(timer)
                                print("Car should have turned left by now")
                                break
                            elif text == 'Move Straight':
                                print("Car shouldn't do anything")
                                break
                            elif text == 'Turn Back':
                                timer *= 2.0
                                right(timer)
                                print("Car should have turned back by now")
                                break
            
                        print(message)
                        sleep(0.2)

            # Reset by pressing CTRL + C
            except KeyboardInterrupt:
                set_PWM(0)
                p1.stop()
                p2.stop()
                GPIO.cleanup()
                cv2.destroyAllWindows()
                print('Autonomus driving stopped')


        elif sys.argv[1] == 'testing':
            print("Testin in 2")
            sleep(2)            
            surface_coef = float(sys.argv[2])
            set_PWM(PWM_FOR_TURNING)
            timer = compute_timer()
            right(timer)
            set_PWM(0)
            p1.stop()
            p2.stop()
            GPIO.cleanup()
            print("Test complete")
        else:
            print("Fuck this program")


    

main()
