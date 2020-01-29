import argparse
import logging
import json
import sys


# Defaults
LOG_FILENAME = "sump_pump_monitor/log/sump_monitor_service.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"


def getConfig(config_file_path):
    with open(config_file_path) as json_file:
        config_json = json.load(json_file)

    return config_json
        


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


def setupLogging(logToFile):
 

    # configure logging for top of "sump" heirarchy, modules will use "sump.module"
    logger = logging.getLogger("sump")

    # set logging level for this top level of heirarchy, can be overridden in modules
    logger.setLevel(logging.DEBUG)

    # add formated stream handler to log to console
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # add formatted file handler to also log to file
    # Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
    file_handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Replace stdout with logging to file at INFO level
    sys.stdout = MyLogger(logger, logging.INFO)
    # Replace stderr with logging to file at ERROR level
    sys.stderr = MyLogger(logger, logging.ERROR)

    # Configure logging level for AWS SDK
    if True:
        aws_logger = logging.getLogger("AWSIoTPythonSDK.core")
        aws_logger.setLevel(logging.INFO)
        aws_logger.addHandler(stream_handler)
        aws_logger.addHandler(file_handler)

