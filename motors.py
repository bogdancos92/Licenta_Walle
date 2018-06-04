import RPi.GPIO as GPIO
from time import sleep
from main_function import p1, p2

#setting left engine pins
LEFT_POZ    = 6
LEFT_NEG    = 13
PWM_LEFT    = 12

#setting right engine pins
RIGHT_POZ   = 20
RIGHT_NEG   = 21
PWM_RIGHT   = 26

#PWM factor
PWM = 0
PWM_FOR_TURNING = 0
PWM_FOR_STRAIGHT = 0

#set global pwm and pwm for motors
def set_PWM(value):
    global PWM
    PWM = value
    p1.ChangeDutyCycle(PWM)
    p2.ChangeDutyCycle(PWM)
    sleep(0.1)

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