# module of sump_monitor functions

import RPi.GPIO as GPIO
import time
import numpy
import logging

logger = logging.getLogger("sump.sumpMonitor")

sump_last_turned_on_time=time.time() # time in seconds as a float
sump_turn_on_counter=0


def log_turn_on(channel):
  global sump_turn_on_counter
  global sump_last_turned_on_time

  sump_turn_on_counter += 1
  sump_last_turned_on_time=time.time()
  logger.info('sump turned on: count: {}'.format(sump_turn_on_counter))

def setup_gpio():
  logger.info("Setup GPIO")
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(23, GPIO.OUT)# ultrasonic trigger
  GPIO.setup(24, GPIO.IN) # ultrasonic echo
  GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP) # sump motor contact
  GPIO.add_event_detect(25, GPIO.RISING, callback=log_turn_on, bouncetime=300)

def getWaterLevel():
    #logger.debug("get water level - single measurement")
    # sensor measures distance down to top of water,
    # need to convert this to height of water level in sump
    # sump is 28 cm deep
    # 15 cm down recorded as roughly 39 
    # max measurement appears to be roughly 49 (quicky filling to 45)
    # y = -9/15x + 48
    
    offset = 49  
    scalingFactor = (39-49)/15;  # sensor reads ~40 cm vs. 28
    start = 0
    stop = 0
    
    #send 1micros trigger pulse
    GPIO.output(23, GPIO.LOW)
    time.sleep(0.00002)
    GPIO.output(23, GPIO.HIGH)
    time.sleep(0.00005)
    GPIO.output(23, GPIO.LOW)

    #measure time time for echo
    for count1 in range(1,10000):
        inp = GPIO.input(24)
        if inp:
            start = time.time()
            break

    for count2 in range(1,10000):
        inp = GPIO.input(24)
        if not inp:
            stop = time.time()
            break

    # distance is proportional to 2x difference in time (there and back)
    mmDistance = round((stop-start)/2*343*100*scalingFactor + offset,1)
    
    return(mmDistance)


def measureSumpWaterLevel():
    logger.debug("measure water level - median of samples measurement")
    numIterations = 10
    waterLevelMeasurements=[]
    for i in range(0,numIterations):
        waterLevelMeasurements.append(getWaterLevel())
        time.sleep(0.1)

    logger.info("measureSumpWaterLevel() - {}".format(waterLevelMeasurements))
    return(numpy.median(waterLevelMeasurements))
        
def cleanup_gpio():
  GPIO.cleanup()
  
if __name__ == "__main__":
  logger.info("testing module")
  setup_gpio()
  logger.info(measureSumpWaterLevel())
  cleanup_gpio()


