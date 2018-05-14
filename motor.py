import RPi.GPIO as GPIO
import time

<<<<<<< HEAD
PIN 	= 18
PWMA1 	= 6 
PWMA2 	= 13
PWMB1 	= 20
PWMB2 	= 21
D1 		= 12
D2 		= 26

PWM 	= 50
=======
PIN = 18
PWMA1 = 6 
PWMA2 = 13
PWMB1 = 20
PWMB2 = 21
D1 = 12
D2 = 26

PWM = 50
>>>>>>> 10f00ce91ccb9c5b89461f00aa23b75ffce97f9b

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
p1.start(50)
p2.start(50)

def	set_motor(A1,A2,B1,B2):
	GPIO.output(PWMA1,A1)
	GPIO.output(PWMA2,A2)
	GPIO.output(PWMB1,B1)
	GPIO.output(PWMB2,B2)
	time.sleep(2)

def forward():
	GPIO.output(PWMA1,1)
	GPIO.output(PWMA2,0)
	GPIO.output(PWMB1,0)
	GPIO.output(PWMB2,1)
	time.sleep(2)	

<<<<<<< HEAD

=======
>>>>>>> 10f00ce91ccb9c5b89461f00aa23b75ffce97f9b
def stop():
	set_motor(0,0,0,0)

def reverse():
	set_motor(0,1,1,0)

def left():
	set_motor(1,0,0,0)

def right():
	set_motor(0,0,0,1)

def functie():
	if True:
		forward()
		print "fwd"
		left()
		print "left"
		right()
		print "right"
		reverse()
		print "reverse"
	GPIO.cleanup()

<<<<<<< HEAD
functie()
=======

functie()
>>>>>>> 10f00ce91ccb9c5b89461f00aa23b75ffce97f9b
