import os
import RPi.GPIO as GPIO
from time import sleep
import time
import distance

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

#surface coefficient
surface_coef = 0.8

#tolerance for distance calibration
tolerance = 1

#setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)

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
p1 = GPIO.PWM(PWM_LEFT,50)
p2 = GPIO.PWM(PWM_RIGHT,50)
p1.start(PWM)
p2.start(PWM)

#let the setup settle
time.sleep(2)

def set_PWM(value):
    global PWM
    PWM = value
    p1.ChangeDutyCycle(PWM)
    p2.ChangeDutyCycle(PWM)

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
    print "RPM = " + str(RPM) + " for PWM = " + str(PWM) + " and voltage = " + str(voltage)
    return RPM

#compute time needed to spin 90 degrees
def compute_timer():
    RPM = compute_RPM()
    # distance to move 130mm
    # one rotation = pi * 65mm = 204
    # 0.637 rotations   ... x sec
    # RPM rotations     ... 60 sec
    # x = 0.637 * 60 sec / RPM
    time = ((0.637 * 60)/RPM)
    print "Time to spin" + str(time)
    return time

#main function for motor control
def set_motor(A1,A2,B1,B2):
    GPIO.output(LEFT_POZ,A1)
    GPIO.output(LEFT_NEG,A2)
    GPIO.output(RIGHT_POZ,B1)
    GPIO.output(RIGHT_NEG,B2)
    # sleep(timer)

#direction control functions
def stop():
    set_motor(0,0,0,0)
    set_PWM(0)

def forward():
    set_motor(1,0,0,1)
    set_PWM(80)

def reverse():
    set_motor(0,1,1,0)
    set_PWM(55)

def left():
    set_motor(1,0,1,0)
    set_PWM(50)

def right():
    set_motor(0,1,0,1)
    set_PWM(50)

#attempt to calibrate surface sensor
def calibrate():
    global surface_coef
    #get initial reference
    initial_distance = distance.compute()
    initial_distance += distance.compute()
    initial_distance += distance.compute()
    initial_distance /= 3

    minimum_distance = initial_distance - tolerance
    maximum_distance = initial_distance + tolerance

    right()

    #set start time
    StartTime = time.time()
    StopTime = time.time()

    while True:
        current_measurement = distance.compute()
        if current_measurement >= minimum_distance and current_measurement <= maximum_distance:
            stop()
            StopTime = time.time()
            break

    TimeElapsed = StopTime - StartTime
    set_PWM(50)
    EngineeredTime = compute_timer()
    EngineeredTime *= 4
    set_PWM(0)

    print str(TimeElapsed) + " should be equal to " + str(EngineeredTime)

    surface_coef = TimeElapsed/EngineeredTime

    print "Surface coeficient is " + str(surface_coef)

#kind of a main function
def main():
    if True:
        calibrate()
        sleep(1)
        set_PWM(50)
        turn_time = compute_timer()
        set_PWM(0)
        turn_time *= surface_coef
        print "Turn for " + str(turn_time)
        sleep(1)
        right()
        sleep(turn_time)
        stop()
        print "Thats all folks"
        GPIO.cleanup()
        sleep(1)

main()
