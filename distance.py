#Libraries
import RPi.GPIO as GPIO
import time

# #GPIO Mode (BOARD / BCM)
# GPIO.setmode(GPIO.BCM)
 
# #set GPIO Pins for front ultrasonic sensor
# GPIO_TRIGGER_FRONT  = 17
# GPIO_ECHO_FRONT     = 18

# #set GPIO Pins for side ultrasonic sensor
# GPIO_TRIGGER_SIDE   = 22
# GPIO_ECHO_SIDE      = 23
 
# #set GPIO direction (IN / OUT)
# GPIO.setup(GPIO_TRIGGER_FRONT, GPIO.OUT)
# GPIO.setup(GPIO_ECHO_FRONT, GPIO.IN)
# GPIO.setup(GPIO_TRIGGER_SIDE, GPIO.OUT)
# GPIO.setup(GPIO_ECHO_SIDE, GPIO.IN)

#let sensors settle
# time.sleep(0.5)
 
def compute(Trigger, Echo):
    #print ("Entering function with pin %d and pin %d", Trigger, Echo)
    # set Trigger to HIGH
    GPIO.output(Trigger, True)

    # set Trigger after 0.05ms to LOW
    time.sleep(0.00005)
    GPIO.output(Trigger, False)
 
    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(Echo) == 0:
        StartTime = time.time()
        TimeElapsed = StartTime - StopTime
        if TimeElapsed > 3:
            break

    # save time of arrival
    while GPIO.input(Echo) == 1:
        StopTime = time.time()
        TimeElapsed = StopTime - StartTime
        if TimeElapsed > 3:
            break

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    #distance in cm
    return distance
 

#for test purposes
# if __name__ == '__main__':
#     try:
#         while True:            
#             #print ("Side")
#             #dist_side = distance(GPIO_TRIGGER_SIDE, GPIO_ECHO_SIDE)
#             #print ("Measured Distance on the right side = %.1f cm" % dist_side)
#             #time.sleep(2)
#             print ("Front")
#             dist_front = distance(GPIO_TRIGGER_FRONT, GPIO_ECHO_FRONT)
#             print ("Measured Distance in front = %.1f cm" % dist_front)
#             time.sleep(2)
            
            
 
#         # Reset by pressing CTRL + C
#     except KeyboardInterrupt:
#         print("Measurement stopped by User")
#         GPIO.cleanup()