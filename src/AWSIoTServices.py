# setup logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import json

logger = logging.getLogger("sump.AWSIoTService")

AWSIOT_CLIENT = None
AWSIOT_CLIENT_CONNECTED = False
AWSIOT_DISCONNECT_COUNT = 0
AWSIOT_ERROR_COUNT = 0

def onClientConnected():
    logger.debug("client online")
    global AWSIOT_CLIENT_CONNECTED 
    AWSIOT_CLIENT_CONNECTED = True

def onClientDisconnected():
    global AWSIOT_CLIENT_CONNECTED, DISCONNECT_COUNT
    AWSIOT_CLIENT_CONNECTED = False
    AWSIOT_DISCONNECT_COUNT += 1

    logger.debug("client offline {} times".format(DISCONNECT_COUNT))

# Custom MQTT message callback
def customCallback(client, userdata, message):
    logger.info ("Topic {} received a new message {}".format(message.topic,message.payload))
    

def setupAWSClient(config_json):    
    logger.debug("setting up device connection to AWS")

    # Init AWSIoTMQTTClient
    global AWSIOT_CLIENT
    AWSIOT_CLIENT = AWSIoTMQTTClient(config_json["awsIoT"]["clientId"])
    AWSIOT_CLIENT.configureEndpoint(config_json["awsIoT"]["endpoint"], config_json["awsIoT"]["port"])
    AWSIOT_CLIENT.configureCredentials(
        config_json["awsIoT"]["rootCACertFile"], 
        config_json["awsIoT"]["privateKeyFile"], 
        config_json["awsIoT"]["certificateFile"])

    # AWSIoTMQTTClient connection configuration
    AWSIOT_CLIENT.configureAutoReconnectBackoffTime(1, 32, 20)
    # Infinite offline Publish queueing
    #AWSIOT_CLIENT.configureOfflinePublishQueueing(-1)
    #AWSIOT_CLIENT.configureDrainingFrequency(2)  # Draining: 2 Hz
    AWSIOT_CLIENT.configureConnectDisconnectTimeout(10)  # 10 sec
    AWSIOT_CLIENT.configureMQTTOperationTimeout(5)  # 5 sec

    # track connection status
    AWSIOT_CLIENT.onOnline = onClientConnected
    AWSIOT_CLIENT.onOffline = onClientDisconnected


def sendMessage(topic, message):
    logger.info("sending message to AWS")

    # Connect and subscribe to AWS IoT
    global AWSIOT_CLIENT
    global AWSIOT_CLIENT_CONNECTED
    global AWSIOT_DISCONNECT_COUNT
    global AWSIOT_ERROR_COUNT

    # add disconnect count to message
    messageJson = json.loads(message)
    messageJson["disconnectCount"] = AWSIOT_DISCONNECT_COUNT
    messageJson["errorCount"] = AWSIOT_ERROR_COUNT

    try:
        if not AWSIOT_CLIENT_CONNECTED:
            connect()

        AWSIOT_CLIENT.publish(topic, json.dumps(messageJson), 1)
    except Exception as e:
        AWSIOT_ERROR_COUNT +=1
        logger.error("Could not publish message to topic {} : {}".format(topic, e))


def listenForMessages(topic):
    # Connect and subscribe to AWS IoT
    global AWSIOT_CLIENT, AWSIOT_ERROR_COUNT
    try:
        if not AWSIOT_CLIENT_CONNECTED:
            connect()

        AWSIOT_CLIENT.subscribe(topic, 1, customCallback)
        logger.info("listening for messages from AWS on topic {}".format(topic))
    except Exception as e:
        AWSIOT_ERROR_COUNT +=1
        logger.error("Could not subscribe to topic {}: {}".format(topic, e))

def connect():
    # Connect and subscribe to AWS IoT
    global AWSIOT_CLIENT, AWSIOT_ERROR_COUNT
    try:
        AWSIOT_CLIENT.connect()
    except Exception as e:
        AWSIOT_ERROR_COUNT +=1
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
