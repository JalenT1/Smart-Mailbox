from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import RPi.GPIO as GPIO
import logging
import time
import argparse
import json

from datetime import datetime

host = "YOUR HOST ADDRESS"
certPath = "CERT FOLDER LOCATION"
clientId = "DEVICE NAME"
topic = "TOPIC NAME"

DOOR_PIN = 17
MAIL_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MAIL_PIN, GPIO.IN)

# Init AWSIoTMQTTClient

myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(
        "{}RootCA1.pem".format(certPath),
        "{}RaspberryPi-private.pem.key".format(certPath),
        "{}RaspberryPi-cert.pem.crt".format(certPath))

# AWSIoTMQTTClient connection configuration

myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
myAWSIoTMQTTClient.connect()

# Publish to the same topic in a loop forever
# Initialize SenseHAT

lastDoorState = None
lastMailState = None
sequence = 0

while True:

    doorOpen = GPIO.input(DOOR_PIN)
    mail = GPIO.input(MAIL_PIN) == 0
    currentState = "Mail Detected" if mail else "Mailbox Empty"
    doorState = "opened" if doorOpen else "closed"

    if doorOpen != lastDoorState:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        payload = {
            "sequence": sequence,
            "timestamp": timestamp,
            "door": doorState
        }
        messageJson = json.dumps(payload)
        myAWSIoTMQTTClient.publish(topic, messageJson, 1)
        print('Published topic %s: %s\n' % (topic, messageJson))
        lastDoorState = doorOpen
        sequence += 1

    if mail != lastMailState:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        payload = {
            "sequence": sequence,
            "timestamp": timestamp,
            "mail": currentState
        }
        messageJson = json.dumps(payload)
        myAWSIoTMQTTClient.publish(topic, messageJson, 1)
        print('Published topic %s: %s\n' % (topic, messageJson))
        lastMailState = mail
        sequence += 1

    time.sleep(0.5)

myAWSIoTMQTTClient.disconnect()
