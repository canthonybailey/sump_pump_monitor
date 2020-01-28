# setup logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import json

logger = logging.getLogger("sump.AWSIoTService")

myAWSIoTMQTTClient = None
clientConnected = False
DISCONNECT_COUNT = 0

def onClientConnected():
    logger.debug("client online")
    global clientConnected 
    clientConnected = True

def onClientDisconnected():
    global clientConnected, DISCONNECT_COUNT
    clientConnected = False
    DISCONNECT_COUNT += 1

    logger.debug("client offline {} times".format(DISCONNECT_COUNT))

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


def sendMessage(topic, message):
    logger.info("sending message to AWS")

    # Connect and subscribe to AWS IoT
    global myAWSIoTMQTTClient
    global clientConnected
    global DISCONNECT_COUNT

    # add disconnect count to message
    messageJson = json.loads(message)
    messageJson["disconnectCount"] = DISCONNECT_COUNT

    try:
       myAWSIoTMQTTClient.publish(topic, json.dumps(messageJson), 1)
    except Exception as e:
       logger.error("Could not publish message to topic {} : {}".format(topic, e))


def listenForMessages(topic):
    # Connect and subscribe to AWS IoT
    global myAWSIoTMQTTClient
    try:
        myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
        logger.info("listening for messages from AWS on topic {}".format(topic))
    except Exception as e:
        logger.error("Could not subscribe to topic {}".format(topic))

def connect():
    # Connect and subscribe to AWS IoT
    global myAWSIoTMQTTClient
    try:
        myAWSIoTMQTTClient.connect()
    except Exception as e:
        logger.error("Could not connect to AWS IoT: {}".format(e))

    

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
