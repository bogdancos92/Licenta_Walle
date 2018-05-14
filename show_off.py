import os
import RPi.GPIO as GPIO
from time import sleep

PIN = 18
PWMA1 = 6
PWMA2 = 13
PWMB1 = 20
PWMB2 = 21
D1 = 12
D2 = 26

PWM = 80

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)
GPIO.setup(PIN,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(PWMA1,GPIO.OUT)
GPIO.setup(PWMA2,GPIO.OUT)
GPIO.setup(PWMB1,GPIO.OUT)
GPIO.setup(PWMB2,GPIO.OUT)
GPIO.setup(D1,GPIO.OUT)
GPIO.setup(D2,GPIO.OUT)
p1 = GPIO.PWM(D1,500)
p2 = GPIO.PWM(D2,500)
p1.start(PWM)
p2.start(PWM)

def set_motor(A1,A2,B1,B2):
        GPIO.output(PWMA1,A1)
        GPIO.output(PWMA2,A2)
        GPIO.output(PWMB1,B1)
        GPIO.output(PWMB2,B2)

def forward(timer):
        set_motor(1,0,0,1)
	sleep(timer)

def stop():
        set_motor(0,0,0,0)

def reverse(timer):
        set_motor(0,1,1,0)
	sleep(timer)

def left(timer):
        set_motor(1,0,0,0)
	sleep(timer)

def right(timer):
        set_motor(0,0,0,1)
	sleep(timer)

def rotate(timer):
	set_motor(1,0,1,0)
	sleep(timer)

def functie():
        if True:
		sleep(0.5)
		stop()
	        os.system('amixer set PCM -- 100%')
	        os.system('mpg123 -q start_v12.mp3 &')
	        print "RRRRRRRRROAAAAAAAAAARRRRRRR"
	        sleep(21)
		print"Entry song"
		os.system('mpg123 -q song.mp3 &')
		sleep(3)
                forward(2)
                print "fwd"
                rotate(1)
		forward(1)
		rotate(3)
                print "360"
		sleep(2)
        GPIO.cleanup()


functie()

