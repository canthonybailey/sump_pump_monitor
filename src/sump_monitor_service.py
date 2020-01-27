#!/usr/bin/env python
 
import logging
import logging.handlers
import argparse
import sys
import json
import time  # this is only being used as part of the example

# include sub modules
import sumpMonitor
import AWSIoTServices
import setupEnvironment

logger = logging.getLogger()

setupEnvironment.setupLogging(False)
args = setupEnvironment.getCommandLineArgs()
AWSIoTServices.setupAWSClient(args)
topic = "bailey/sump/status"
AWSIoTServices.listenForMessages(topic)

sumpMonitor.setup_gpio()

while True:
    cmDistance = round(sumpMonitor.measureSumpWaterLevel(),1)

    mins_since_last_pump=round((time.time()-sumpMonitor.sump_last_turned_on_time)/60,1)

    payload={}
    payload["sumpTurnOnCount"]=sumpMonitor.sump_turn_on_counter
    payload["sumpMinSinceLastTurnOn"]=mins_since_last_pump
    payload["sumpWaterLevel"]=cmDistance

    print "publishing device data" + json.dumps(payload)
    
    AWSIoTServices.sendMessage(topic, json.dumps(payload))
    time.sleep(10)


#client.loop_stop();
#client.disconnet();
sumpMonitor.cleanup_gpio();
