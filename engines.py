import RPi.GPIO as GPIO
import time

M3 = 6 
M4 = 13
M1 = 20
M2 = 21
PWMB = 12
PWMA = 26

PWM = 40

def set_motor(A1,A2,A3,A4):
	GPIO.output(M1,A1)
	print "M1 ok"
	GPIO.output(M2,A2)
	print "M2 ok"
	time.sleep(0.05)
	GPIO.output(M3,A3)
	print "M3 ok"
	GPIO.output(M4,A4)
	print "M4 ok"

def forward():
	stop()
	GPIO.output(M3,GPIO.HIGH)
	GPIO.output(M2,GPIO.HIGH)

def stop():
	set_motor(GPIO.LOW,GPIO.LOW,GPIO.LOW,GPIO.LOW)

def reverse():
	set_motor(GPIO.LOW,GPIO.HIGH,GPIO.LOW,GPIO.HIGH)

def left():
	set_motor(GPIO.HIGH,GPIO.LOW,GPIO.LOW,GPIO.LOW)

def right():
	set_motor(GPIO.LOW,GPIO.LOW,GPIO.HIGH,GPIO.LOW)

def functie():
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(True)
	GPIO.setup(M1,GPIO.OUT)
	GPIO.setup(M2,GPIO.OUT)
	GPIO.setup(M3,GPIO.OUT)
	GPIO.setup(M4,GPIO.OUT)
	GPIO.setup(PWMA,GPIO.OUT)
	GPIO.setup(PWMB,GPIO.OUT)
	p1 = GPIO.PWM(PWMA,500)
	p2 = GPIO.PWM(PWMB,500)
	p1.start(PWM)
	p2.start(PWM)

	if True:
		time.sleep(3)
		p1.ChangeDutyCycle(33)
	        p2.ChangeDutyCycle(33)
		forward()
		print "fwd"
		time.sleep(2)
		p1.ChangeDutyCycle(75)
	        p2.ChangeDutyCycle(25)
		#stop()
		#time.sleep(2)
		reverse()
		print "rev"
		time.sleep(2)
		#stop()
		#time.sleep(2)
		right()
		print "right"
		time.sleep(2)
		#stop()
		#time.sleep(2)
		left()
		print "left"
		time.sleep(2)
		#stop()
		#time.sleep(2)

functie()
GPIO.cleanup()
