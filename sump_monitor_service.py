#!/usr/bin/env python
 
import logging
import logging.handlers
import argparse
import sys
import time  # this is only being used as part of the example
 
# Deafults
LOG_FILENAME = "/tmp/sump_monitor_service.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"
 
# Define and parse command line arguments
parser = argparse.ArgumentParser(description="My simple Python service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")
 
# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
	LOG_FILENAME = args.log
 
# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)
 
# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
	def __init__(self, logger, level):
		"""Needs a logger and a logger level."""
		self.logger = logger
		self.level = level
 
	def write(self, message):
		# Only log if there is a message (not just a new line)
		if message.rstrip() != "":
			self.logger.log(self.level, message.rstrip())
 
# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)
 

import RPi.GPIO as GPIO
import dweepy
import time

logger.info("setting up GPIO")
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)# ultrasonic trigger
GPIO.setup(24, GPIO.IN) # ultrasonic echo
#GPIO.setup(12, GPIO.IN) # sump motor contact

sump_last_turned_on_time=time.time() # time in seconds as a float
sump_turn_on_counter=0
water_level=0
dweet_thing_name='canton_bailey_sump'

def printFunction(status):
  dweepy.dweet_for(dweet_thing_name,{'status':status})

def log_turn_on(channel):
  global sump_turn_on_counter
  global sump_last_turned_on_time

  sump_turn_on_counter += 1
  sump_last_turned_on_time=time.time()
  logger.info('sump turned on: count: ' + str(sump_turn_on_counter)) 
  printFunction('turned on' + str(sump_turn_on_counter))

#GPIO.add_event_detect(12, GPIO.FALLING, callback=log_turn_on, bouncetime=300)

start=0
stop=0

while True:
    #send 1micros trigger pulse to triger send
    GPIO.output(23, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(23, GPIO.LOW)

    #measure time between start and stop of echo
    for count1 in xrange(10000):
        inp = GPIO.input(24)
        if inp:
            start = time.time()
            break

    for count2 in xrange(10000):
        inp = GPIO.input(24)
        if not inp:
            stop = time.time()
            break

    # distance is proportional to 
    deltaT = stop - start
    cmDistance = round(deltaT/2*343*100,1)

    mins_since_last_pump=round((time.time()-sump_last_turned_on_time)/60,1)
    dweepy.dweet_for(dweet_thing_name,{'sump_counter':sump_turn_on_counter, 'minutes_since':mins_since_last_pump, 'water_level':cmDistance})
    time.sleep(10)

GPIO.cleanup()
