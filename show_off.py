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
PWM = 80

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
    set_motor(1,0,0,0,timer)

def right(timer):
    set_motor(0,0,0,1,timer)

def rotate(timer):
	set_motor(1,0,1,0,timer)

#kind of a maine function
def functie():
    if True:
		sleep(0.5)
		stop()
		print "stop"
		sleep(0.5)
    	forward(1)
    	print "fwd 1"
    	rotate(1)
    	print "rotate 1"
		forward(1)
		print "fwd 1"
		rotate(2)
    	print "rotate 2"
    	left(1)
    	print "left 1"
    	right(1)
    	print "right 1"
    	sleep(2)
   	GPIO.cleanup()


functie()
