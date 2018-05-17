#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER_FRONT  = 17
GPIO_ECHO_FRONT     = 18
GPIO_TRIGGER_SIDE   = 22
GPIO_ECHO_SIDE      = 23
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER_FRONT, GPIO.OUT)
GPIO.setup(GPIO_ECHO_FRONT, GPIO.IN)
GPIO.setup(GPIO_TRIGGER_SIDE, GPIO.OUT)
GPIO.setup(GPIO_ECHO_SIDE, GPIO.IN)
 
def distance(Trigger, Echo):
    # set Trigger to HIGH
    GPIO.output(Trigger, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(Trigger, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(Echo) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(Echo) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        while True:
            dist = distance(GPIO_TRIGGER_FRONT, GPIO_ECHO_FRONT)
            print ("Measured Distance in front = %.1f cm" % dist)
            time.sleep(1)
            dist = distance(GPIO_TRIGGER_SIDE, GPIO_ECHO_SIDE)
            print ("Measured Distance on the right side = %.1f cm" % dist)
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()