#Libraries
import RPi.GPIO as GPIO
from time import sleep
import config

global p1
global p2

#set global pwm and pwm for motors
def set_PWM(value):
    config.PWM = value
    p1.ChangeDutyCycle(config.PWM)
    p2.ChangeDutyCycle(config.PWM)
    sleep(0.1)

#main function for motor control
def set_motor(A1,A2,B1,B2):
    GPIO.output(config.LEFT_POZ,A1)
    GPIO.output(config.LEFT_NEG,A2)
    GPIO.output(config.RIGHT_POZ,B1)
    GPIO.output(config.RIGHT_NEG,B2)
        
#direction control functions
def stop():
    set_motor(0,0,0,0)
    set_PWM(0)
    print("Stop")

def forward():
    set_motor(1,0,0,1)
    set_PWM(config.PWM_FOR_STRAIGHT)
    print("Straight")

def reverse(timer):
    set_motor(1,0,1,0)
    set_PWM(config.PWM_FOR_TURNING)
    print("Turning around")
    sleep(timer)
    stop()

def right(timer):
    set_motor(1,0,1,0)
    set_PWM(config.PWM_FOR_TURNING)
    print("Turning right")
    sleep(timer)
    stop()

def left(timer):
    set_motor(0,1,0,1)
    set_PWM(config.PWM_FOR_TURNING)
    print("Turning left")
    sleep(timer)
    stop()