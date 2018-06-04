import os
import RPi.GPIO as GPIO
from time import sleep
import time
import numpy as np
import cv2
import sys

#import other files
import motors
import distance
import traffic_recognition

#set GPIO Pins for front ultrasonic sensor
GPIO_TRIGGER_FRONT  = 17
GPIO_ECHO_FRONT     = 18

#set GPIO Pins for side ultrasonic sensor
GPIO_TRIGGER_SIDE   = 22
GPIO_ECHO_SIDE      = 23

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

#state machine states
STATES = [
        'initial',
        'move_straight',
        'check_distance',
        'check_for_sign',
        'end'
    ]

# define range HSV for blue color of the traffic sign
lower_blue = np.array([85,100,70])
upper_blue = np.array([115,255,255])

camera = cv2.VideoCapture(0)

p1 = 0
p2 = 0

#set all pins and initialize pwms
def initial_setup():
    global p1
    global p2

    #setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    #left motor setup
    GPIO.setup(motors.LEFT_POZ,GPIO.OUT)
    GPIO.setup(motors.LEFT_NEG,GPIO.OUT)
    GPIO.setup(motors.PWM_LEFT,GPIO.OUT)
    
    #right motor setup
    GPIO.setup(motors.RIGHT_POZ,GPIO.OUT)
    GPIO.setup(motors.RIGHT_NEG,GPIO.OUT)
    GPIO.setup(motors.PWM_RIGHT,GPIO.OUT)
    
    #ultrasonic setup
    GPIO.setup(GPIO_TRIGGER_FRONT, GPIO.OUT)
    GPIO.setup(GPIO_ECHO_FRONT, GPIO.IN)
    GPIO.setup(GPIO_TRIGGER_SIDE, GPIO.OUT)
    GPIO.setup(GPIO_ECHO_SIDE, GPIO.IN)
    
    #frequency setup
    p1 = GPIO.PWM(motors.PWM_LEFT,500)
    p2 = GPIO.PWM(motors.PWM_RIGHT,500)
    p1.start(motors.PWM)
    p2.start(motors.PWM)
    

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
    voltage = map(motors.PWM_FOR_TURNING, 0, 100, 0.0, 6.0)
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
    print('RPM = ' + str(RPM) + ' for PWM_FOR_TURNING = ' + str(motors.PWM_FOR_TURNING) + ' and voltage = ' + str(voltage))
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

#kind of a main function
def main():
    print('In main function')
    
    if len(sys.argv) is 5:
        if sys.argv[1] == 'start':

            #initialize configurable data
            surface_coef = float(sys.argv[2])
            motors.PWM_FOR_TURNING = int(sys.argv[3])
            motors.PWM_FOR_STRAIGHT = int(sys.argv[4])

            try:
                state = 'initial'

                while state in STATES:

                    if state == 'initial' :
                        print("--------------Initial state--------------")

                        initial_setup()
                        print("Setup done")
                        sleep(2)
                        state = 'move_straight'
                        #end of initial state

                    elif state == 'move_straight' :
                        print("--------------Forward state--------------")

                        #Start car
                        motors.forward()
                        state = 'check_distance'
                        #end of move_straight state

                    elif state == 'check_distance' :
                        print("---------Checking distance state---------")

                        #calculate distance from sign
                        remaining_distance = average_distance()
                        
                        #while distance is less than the desired distance, keep going
                        while remaining_distance > distance_from_sign:

                            remaining_distance = distance.compute(GPIO_TRIGGER_FRONT, GPIO_ECHO_FRONT)

                            if remaining_distance < distance_from_sign:
                                motors.stop()
                                sleep(1)
                                break
                        state = 'check_for_sign'
                        #end of check_distance state

                    elif state == 'check_for_sign' :
                        print("--------Checking for a sign state--------")

                        StartTime = time.time()
                        StopTime = time.time()

                        while True:
                            StopTime = time.time()
                            ElapsedTime = StopTime - StartTime

                            if ElapsedTime > 5 :
                                state = 'end'
                                break
                            else :
                                text = traffic_recognition.findTrafficSign(camera, lower_blue, upper_blue)
                                message = text

                                if text in TRAFFIC_SIGNS:        
                                    #Traffic sign found
                                    message = 'Found sign --------- ' + text        
                                    #compute time to spin
                                    timer = compute_timer()        
                                    #choose direction to follow

                                    if text == 'Turn Right':
                                        motors.right(timer)
                                        print("Car should have turned right by now")
                                        state = 'move_straight'
                                        break

                                    elif text == 'Turn Left':
                                        motors.left(timer)
                                        print("Car should have turned left by now")
                                        state = 'move_straight'
                                        break

                                    elif text == 'Move Straight':
                                        print("Car shouldn't do anything")
                                        state = 'move_straight'
                                        break

                                    elif text == 'Turn Back':
                                        timer *= 2.0
                                        motors.right(timer)
                                        print("Car should have turned back by now")
                                        state = 'move_straight'
                                        break

                        print(message)
                        sleep(1)
                        #end of check_for_sign state

                    elif state == 'end' :
                        print("-----------------The End-----------------")
                        print("No image found")
                        motors.set_PWM(0)
                        p1.stop()
                        p2.stop()
                        GPIO.cleanup()
                        cv2.destroyAllWindows()
                        print("End of program")
                        sys.exit(0)
                        #end of end state

                    else:
                        #well this is not supposed to ever come up
                        print("State not implemented")
                        motors.set_PWM(0)
                        p1.stop()
                        p2.stop()
                        GPIO.cleanup()
                        cv2.destroyAllWindows()
                        print("End of program")
                        sys.exit(0)

            # Reset by pressing CTRL + C
            except KeyboardInterrupt:
                motors.set_PWM(0)
                p1.stop()
                p2.stop()
                GPIO.cleanup()
                cv2.destroyAllWindows()
                print('Autonomus driving stopped')


        elif sys.argv[1] == 'testing':
            print("Testin in 2")
            sleep(2)            
            surface_coef = float(sys.argv[2])
            motors.set_PWM(PWM_FOR_TURNING)
            timer = compute_timer()
            motors.set_PWM(0)
            right(timer)
            motors.stop()
            p1.stop()
            p2.stop()
            GPIO.cleanup()
            print("Test complete")

        else:
            print("Fuck this program")
#Let the fun begin
main()
