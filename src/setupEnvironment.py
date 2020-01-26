import argparse
import logging

# Defaults
LOG_FILENAME = "/tmp/sump_monitor_service.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

AllowedActions = ['both', 'publish', 'subscribe']


def getCommandLineArgs():
    global LOG_FILENAME

    # Read in command-line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True,
                        dest="host", help="Your AWS IoT custom endpoint")
    parser.add_argument("-r", "--rootCA", action="store",
                        required=True, dest="rootCAPath", help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store",
                        dest="certificatePath", help="Certificate file path")
    parser.add_argument("-k", "--key", action="store",
                        dest="privateKeyPath", help="Private key file path")
    parser.add_argument("-p", "--port", action="store",
                        dest="port", type=int, help="Port number override")
    parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                        help="Use MQTT over WebSocket")
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                        help="Targeted client id")
    parser.add_argument("-t", "--topic", action="store", dest="topic",
                        default="sdk/test/Python", help="Targeted topic")
    parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
                        help="Operation modes: %s" % str(AllowedActions))
    parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                        help="Message to publish")
    parser.add_argument("-l", "--log", dest="log", help="file to write log to (default '%s')" %(LOG_FILENAME))


    args = parser.parse_args()

    if args.mode not in AllowedActions:

        parser.error("Unknown --mode option %s. Must be one of %s" %
                     (args.mode, str(AllowedActions)))
        exit(2)

    # If the log file is specified on the command line then override the default
    if args.log:
        LOG_FILENAME = args.log

    return args


def setupLogging(logToFile):
 

    # Format each log message like this
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
    # Give the logger a unique name (good practice)
    #logger = logging.getLogger(__name__)
    # Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
    #handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
    # Attach the formatter to the handler
    #handler.setFormatter(formatter)
    # Attach the handler to the logger
    #logger.addHandler(handler)
    #logging.FileHandler()

    # Configure logging
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(LOG_LEVEL)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)


 
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
#sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
#sys.stderr = MyLogger(logger, logging.ERROR)
