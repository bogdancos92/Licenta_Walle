import os
import RPi.GPIO as GPIO
from time import sleep

#setting left engine pins
LEFT_POZ 	= 6
LEFT_NEG 	= 13
PWM_LEFT 	= 12

#setting right engine pins
RIGHT_POZ 	= 20
RIGHT_NEG 	= 21
PWM_RIGHT 	= 26

#PWM factor
PWM = 50

#surface coefficient
surface_coef = 1.0

#wheeldiameter
wheel_diameter = 65 #mm


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

#frequency setup
p1 = GPIO.PWM(PWM_LEFT,500)
p2 = GPIO.PWM(PWM_RIGHT,500)
p1.start(PWM)
p2.start(PWM)

def set_PWM(value):
    p1.ChangeDutyCycle(value)
    p2.ChangeDutyCycle(value)

def map(x, in_min, in_max, out_min, out_max):
    value = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    return value


def compute_RPM():
    #3V...125RPM
    #5V...200RPM
    #6V...230RPM
    voltage = map(PWM, 0, 100, 0, 6)
    if voltage < 3:
        voltage = 3
        RPM = 125
    elif voltage >= 3 and voltage < 5:
        RPM = map (voltage, 3, 5 , 125, 200)
    elif voltage >=5 and voltage < 6:
        RPM = map (voltage, 5, 6 , 200, 230)
    elif voltage >= 6:
        voltage = 6
        RPM = 230
    print "RPM = " + str(RPM) + " for PWM = " + str(PWM)
    return RPM

def compute_timer():
    RPM = compute_RPM()
    #distance to move 130mm = 2 rotations
    # 2 rotations   ... x sec
    # RPM rotations ... 60 sec
    # x = 120 sec / RPM
    time = 120.0/RPM * surface_coef
    print "Time to spin" + str(time)
    return time

#main function for motor control
def set_motor(A1,A2,B1,B2,timer):
    GPIO.output(LEFT_POZ,A1)
    GPIO.output(LEFT_NEG,A2)
    GPIO.output(RIGHT_POZ,B1)
    GPIO.output(RIGHT_NEG,B2)
    sleep(timer)

#direction control functions
def stop():
    set_motor(0,0,0,0,0)

def forward(timer):
    set_motor(1,0,0,1,timer)

def reverse(timer):
    set_motor(0,1,1,0,timer)

def left(timer):
    set_motor(1,0,1,0,timer)

def right(timer):
    set_motor(0,1,0,1,timer)

#kind of a main function
def main():
    if True:
        stop()
        print "stop"
        sleep(2)
        timer = compute_timer()
        right(timer)
        stop()
        print "Now wait 3 sec"
        set_PWM(80)
        sleep(3)        
        timer = compute_timer()
        left(timer)
        print "Now wait 3 sec"
        stop()
        sleep(3)
        print "Thats all folks"
        GPIO.cleanup()
        sleep(1)


main()
