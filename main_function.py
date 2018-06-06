#Libraries
import os
import RPi.GPIO as GPIO
from time import sleep
import time
import numpy as np
import cv2
import sys

#import other files
import distance
import traffic_recognition
import config
import motors

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
        'check_distance',
        'check_for_sign',
        'end'
    ]

# define range HSV for blue color of the traffic sign
lower_blue = np.array([85,100,70])
upper_blue = np.array([115,255,255])

camera = cv2.VideoCapture(0)

#set all pins and initialize pwms
def initial_setup():

    #setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    #left motor setup
    GPIO.setup(config.LEFT_POZ,GPIO.OUT)
    GPIO.setup(config.LEFT_NEG,GPIO.OUT)
    GPIO.setup(config.PWM_LEFT,GPIO.OUT)
    
    #right motor setup
    GPIO.setup(config.RIGHT_POZ,GPIO.OUT)
    GPIO.setup(config.RIGHT_NEG,GPIO.OUT)
    GPIO.setup(config.PWM_RIGHT,GPIO.OUT)
    
    #ultrasonic setup
    GPIO.setup(config.GPIO_TRIGGER_FRONT, GPIO.OUT)
    GPIO.setup(config.GPIO_ECHO_FRONT, GPIO.IN)
    GPIO.setup(config.GPIO_TRIGGER_SIDE, GPIO.OUT)
    GPIO.setup(config.GPIO_ECHO_SIDE, GPIO.IN)
    
    #frequency setup
    motors.p1 = GPIO.PWM(config.PWM_LEFT,500)
    motors.p2 = GPIO.PWM(config.PWM_RIGHT,500)
    motors.p1.start(config.PWM)
    motors.p2.start(config.PWM)
    
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
    voltage = map(config.PWM_FOR_TURNING, 0, 100, 0.0, 6.0)
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
    #print('RPM = ' + str(RPM) + ' for PWM_FOR_TURNING = ' + str(config.PWM_FOR_TURNING) + ' and voltage = ' + str(voltage))
    return RPM

#compute time needed to spin 90 degrees
def compute_timer():
    global surface_coef
    RPM = compute_RPM()
    # distance to move 130mm
    # one rotation = pi * 65mm = 204
    # 0.637 rotations   ... x sec
    # RPM rotations     ... 60 sec
    # x = 0.637 * 60 sec / RPM
    time = ((0.637 * 60.0)/RPM) * surface_coef
    # print ('Time to spin ... ' + str(time))
    return time

#compute average distance
def average_distance():
    average = distance.compute(config.GPIO_TRIGGER_FRONT, config.GPIO_ECHO_FRONT)
    average += distance.compute(config.GPIO_TRIGGER_FRONT, config.GPIO_ECHO_FRONT)
    average /= 2
    return average

#kind of a main function
def main():
    global surface_coef
    global distance_from_sign

    print('In main function')
    
    if len(sys.argv) is 6:

        #initialize configurable data
        surface_coef = float(sys.argv[2])
        config.PWM_FOR_TURNING = int(sys.argv[3])
        config.PWM_FOR_STRAIGHT = int(sys.argv[4])
        distance_from_sign = int(sys.argv[5])

        if sys.argv[1] == 'start':

            try:
                state = 'initial'

                while state in STATES:

                    if state == 'initial' :
                        print("--------------Initial state--------------")

                        initial_setup()
                        print("Setup done")
                        sleep(2)
                        state = 'check_distance'
                        #end of initial state

                    elif state == 'check_distance' :
                        print("---------Checking distance state---------")

                        #calculate distance from sign
                        remaining_distance = average_distance()

                        if config.PWM == 0:
                            if remaining_distance > (0.8 * distance_from_sign):
                                print("Car is stopped and motors are set to on")
                                motors.forward()
                                print("Car is moving")
                                sleep(0.2)
                                #while distance is less than the desired distance, keep going
                                while remaining_distance > distance_from_sign:

                                    remaining_distance = distance.compute(config.GPIO_TRIGGER_FRONT, config.GPIO_ECHO_FRONT)

                                    if remaining_distance < distance_from_sign:
                                        motors.stop()
                                        sleep(1)
                                        break
                            else:
                                print("Car is stopped and sign shoud be in front")
                        
                        state = 'check_for_sign'   
                        #end of check_distance state

                    elif state == 'check_for_sign' :
                        print("--------Checking for a sign state--------")

                        StartTime = time.time()
                        StopTime = time.time()

                        text = 'None'

                        while True:
                            StopTime = time.time()
                            ElapsedTime = StopTime - StartTime

                            if ElapsedTime > 5 :
                                print("No image found")
                                state = 'end'
                                break
                            else :
                                text = str(traffic_recognition.findTrafficSign(camera, lower_blue, upper_blue))
                                message = text

                                if text in TRAFFIC_SIGNS:        
                                    #Traffic sign found
                                    message = 'Found sign --------- ' + text
                                    print(message)        
                                    #compute time to spin
                                    timer = compute_timer()        
                                    #choose direction to follow

                                    if text == 'Turn Right':
                                        motors.right(timer)
                                        print("Car should have turned right by now")
                                        state = 'check_distance'
                                        break

                                    elif text == 'Turn Left':
                                        motors.left(timer)
                                        print("Car should have turned left by now")
                                        state = 'check_distance'
                                        break

                                    elif text == 'Move Straight':
                                        print("Car should stop now")
                                        state = 'end'
                                        break

                                    elif text == 'Turn Back':
                                        motors.reverse(timer)
                                        print("Car should have turned back by now")
                                        state = 'check_distance'
                                        break
                                else:
                                    print(message)
                        
                        sleep(1)
                        #end of check_for_sign state

                    elif state == 'end' :
                        print("-----------------The End-----------------")
                        motors.stop()
                        motors.p1.stop()
                        motors.p2.stop()
                        GPIO.cleanup()
                        cv2.destroyAllWindows()
                        print("End of program")
                        sys.exit(0)
                        #end of end state

                    else:
                        #well this is not supposed to ever come up
                        print("State not implemented")
                        motors.stop()
                        motors.p1.stop()
                        motors.p2.stop()
                        GPIO.cleanup()
                        cv2.destroyAllWindows()
                        print("End of program")
                        sys.exit(0)

            # Reset by pressing CTRL + C
            except KeyboardInterrupt:
                motors.stop()
                motors.p1.stop()
                motors.p2.stop()
                GPIO.cleanup()
                cv2.destroyAllWindows()
                print('Autonomus driving stopped')


        elif sys.argv[1] == 'testing':
            initial_setup()
            print("Testin in 2")
            sleep(2)
            print("surface_coef is "  + str(surface_coef))
            timer = compute_timer()
            motors.right(timer)
            motors.p1.stop()
            motors.p2.stop()
            GPIO.cleanup()
            print("Test complete")

        else:
            print("Unknown argument")

    elif sys.argv[1] == 'camera':

        try:
            state = 'initial'

            while state in STATES:

                if state == 'initial' :
                    print("--------------Initial state--------------")
                    initial_setup()
                    print("Setup done")
                    sleep(2)
                    state = 'check_distance'
                    #end of initial state

                elif state == 'check_distance' :
                    print("---------Checking distance state---------")
                    #calculate distance from sign
                    remaining_distance = average_distance()

                    if config.PWM == 0:
                        if remaining_distance > (0.8 * distance_from_sign):
                            print("Car is stopped and motors are set to on")
                            print("Car is moving")
                            sleep(0.2)
                            #while distance is less than the desired distance, keep going
                            while remaining_distance > distance_from_sign:
                                remaining_distance = distance.compute(config.GPIO_TRIGGER_FRONT, config.GPIO_ECHO_FRONT)
                                if remaining_distance < distance_from_sign:
                                    sleep(1)
                                    break
                        else:
                            print("Car is stopped and sign shoud be in front")
                    
                    state = 'check_for_sign'   
                    #end of check_distance state

                elif state == 'check_for_sign' :
                    print("--------Checking for a sign state--------")

                    StartTime = time.time()
                    StopTime = time.time()

                    text = 'None'

                    while True:
                        
                        StopTime = time.time()
                        ElapsedTime = StopTime - StartTime

                        if ElapsedTime > 5 :
                            print("No image found")
                            state = 'end'
                            break

                        else :
                            text = str(traffic_recognition.findTrafficSign(camera, lower_blue, upper_blue))
                            message = text

                            if text in TRAFFIC_SIGNS:
                                #Traffic sign found
                                message = 'Found sign --------- ' + text
                                print(message)
                                state = 'check_distance'
                                break   
                            else:
                                print(message)

                    
                    sleep(4)
                    #end of check_for_sign state
                elif state == 'end' :
                    print("-----------------The End-----------------")
                    GPIO.cleanup()
                    cv2.destroyAllWindows()
                    print("End of program")
                    sys.exit(0)
                    #end of end state
                else:
                    #well this is not supposed to ever come up
                    print("State not implemented")
                    GPIO.cleanup()
                    cv2.destroyAllWindows()
                    print("End of program")
                    sys.exit(0)
        # Reset by pressing CTRL + C
        except KeyboardInterrupt:
            GPIO.cleanup()
            cv2.destroyAllWindows()
            print('Autonomus driving stopped')

    else:
        print("Something went way to wrong")    


#Let the fun begin
main()
