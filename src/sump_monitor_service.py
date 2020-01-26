#!/usr/bin/env python
 
import logging
import logging.handlers
import argparse
import sys
import time  # this is only being used as part of the example
import sumpMonitor

import paho.mqtt.client as mqtt
import time
import json

 
 

# device registration info from IBM Internet of Things Foundation
org="okx4rp"
mqttHost= org + ".messaging.internetofthings.ibmcloud.com"
mqttPort=1883
deviceType="RaspberryPiMQTT"
deviceId="RaspberryPI-0013efb035a7"
clientId="d:" + org + ":" + deviceType + ":" + deviceId
authMethod="token"
authToken="@MTD+L(n-xeOcqpe?O"
topic="iot-2/evt/sump_monitor_update/fmt/json"

def on_connect(mqttClient, obj, rc):
# log connection and response codes
        logger.info("MQTT Connected Code = %d"%(rc))

def on_disconnect(pahoClient, obj, rc):
# log disconnects
        logger.info("MQTT Disconnected Code = %d"%(rc))

# Create a client instance
client=mqtt.Client(client_id=clientId)

# Register callbacks
client.on_connect = on_connect
client.on_disconnnect = on_disconnect

#Set userid and password
client.username_pw_set("use-token-auth", authToken)

#connect and start background loop
logger.info("connecting MQTT client")
x = client.connect(mqttHost, mqttPort, 60)
client.loop_start()

sumpMonitor.setup_gpio()

while True:
    cmDistance = round(sumpMonitor.measureSumpWaterLevel(),1)

    mins_since_last_pump=round((time.time()-sumpMonitor.sump_last_turned_on_time)/60,1)

    payload={}
    #payload["d"]={} # IoT foundation payload starts with "d" for device
    #payload["myName"]=clientId
    payload["sumpTurnOnCount"]=sumpMonitor.sump_turn_on_counter
    payload["sumpMinSinceLastTurnOn"]=mins_since_last_pump
    payload["sumpWaterLevel"]=cmDistance

    logger.info("publishing device data" + json.dumps(payload))
    client.publish(topic, json.dumps(payload), 0)
    #dweepy.dweet_for(dweet_thing_name,{'sump_counter':sump_turn_on_counter, 'minutes_since':mins_since_last_pump, 'water_level':cmDistance})
    time.sleep(10)


client.loop_stop();
client.disconnet();
sumpMonitor.cleanup_gpio();
