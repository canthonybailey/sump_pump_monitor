#!/usr/bin/env python
 
import logging
import logging.handlers
import argparse
import sys
import json
import os
import time  # this is only being used as part of the example

# include sub modules
import sumpMonitor
import AWSIoTServices
import setupEnvironment

logger = logging.getLogger("sump.sump_monitor_service")

setupEnvironment.setupLogging(False)

# dirpath = os.getcwd()
#logger.info("current directory is : " + dirpath)
#foldername = os.path.basename(dirpath)
#logger.info("Directory name is : " + foldername)

config_json = setupEnvironment.getConfig("sump_pump_monitor/src/config.json")
AWSIoTServices.setupAWSClient(config_json)
AWSIoTServices.connect()

topic = config_json["sumpPumpMonitor"]["topic"]
AWSIoTServices.listenForMessages(topic)

sumpMonitor.setup_gpio()

while True:
    cmDistance = round(sumpMonitor.measureSumpWaterLevel(),1)

    mins_since_last_pump=round((time.time()-sumpMonitor.sump_last_turned_on_time)/60,1)
    status = "Normal" if (mins_since_last_pump <= 120) else "Alert"
    payload={}
    payload["sumpTurnOnCount"]=sumpMonitor.sump_turn_on_counter
    payload["sumpMinSinceLastTurnOn"]=mins_since_last_pump
    payload["sumpWaterLevel"]=cmDistance
    payload["sumpStatus"]=status

    logger.info("publishing device data {}".format(json.dumps(payload)))
    
    AWSIoTServices.sendMessage(topic, json.dumps(payload))
    time.sleep(10)


#client.loop_stop();
#client.disconnet();
sumpMonitor.cleanup_gpio();
