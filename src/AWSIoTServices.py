# setup logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
logger = logging.getLogger("sump.AWSIoTService")

myAWSIoTMQTTClient = None
clientConnected = False

def onClientConnected():
    logger.debug("client online")
    global clientConnected 
    clientConnected = True

def onClientDisconnected():
    logger.debug("client offline")
    global clientConnected 
    clientConnected = False

# Custom MQTT message callback
def customCallback(client, userdata, message):
    logger.info ("Topic {} received a new message {}".format(message.topic,message.payload))
    

def setupAWSClient(config_json):    
    logger.debug("setting up device connection to AWS")

    # Init AWSIoTMQTTClient
    global myAWSIoTMQTTClient
    myAWSIoTMQTTClient = AWSIoTMQTTClient(config_json["awsIoT"]["clientId"])
    myAWSIoTMQTTClient.configureEndpoint(config_json["awsIoT"]["endpoint"], config_json["awsIoT"]["port"])
    myAWSIoTMQTTClient.configureCredentials(
        config_json["awsIoT"]["rootCACertFile"], 
        config_json["awsIoT"]["privateKeyFile"], 
        config_json["awsIoT"]["certificateFile"])

    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    # track connection status
    myAWSIoTMQTTClient.onOnline = onClientConnected
    myAWSIoTMQTTClient.onOffline = onClientDisconnected


def sendMessage(topic, messageJson):
    logger.info("sending message to AWS")

    # Connect and subscribe to AWS IoT
    global myAWSIoTMQTTClient
    global clientConnected

    if clientConnected:
        myAWSIoTMQTTClient.publish(topic, messageJson, 1)
    else:
        logger.error("not connected - can not send")


def listenForMessages(topic):
    logger.info("listening for messages from AWS on topic {}".format(topic))

    # Connect and subscribe to AWS IoT
    global myAWSIoTMQTTClient
    myAWSIoTMQTTClient.connect()
    myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)


# if module invoked directly, do a simple test of AWS IoT Connection
if __name__ == "__main__":

    import time
    import json
    import setupEnvironment

    logger.info("Testing module ")

    setupEnvironment.setupLogging(False)

    # Read in command-line parameters
    config_json = setupEnvironment.getConfig("src/config.json")
    setupAWSClient(config_json)

    topic = config_json["sumpPumpMonitor"]["topic"]
    logger.debug("Read topic from config: {}".format(topic))
    listenForMessages(topic)

    # Publish to the same topic in a loop forever
    loopCount = 0
    while True:

        message = {}
        message['message'] = "testing"
        message['sequence'] = loopCount
        messageJson = json.dumps(message)

        sendMessage(topic, messageJson)
        loopCount = loopCount+1
        time.sleep(10) # change to "sleep() is synchronous, could change to timeout "
