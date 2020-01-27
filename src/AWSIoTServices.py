# setup logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
logger = logging.getLogger()

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

    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


def setupAWSClient(args):    
    logger.debug("setting up device connection to AWS")

    # Init AWSIoTMQTTClient
    global myAWSIoTMQTTClient
    myAWSIoTMQTTClient = AWSIoTMQTTClient(args.clientId)
    myAWSIoTMQTTClient.configureEndpoint(args.host, args.port)
    myAWSIoTMQTTClient.configureCredentials(
        args.rootCAPath, args.privateKeyPath, args.certificatePath)

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
    logger.info("listening for messages from AWS")

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

    setupEnvironment.setupLogging("false")

    # Read in command-line parameters
    args = setupEnvironment.getCommandLineArgs()
    setupAWSClient(args)

    topic = "bailey/sump/status"
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
