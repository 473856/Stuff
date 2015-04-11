#!/usr/bin/python

#
# 1) Read TNode data from mqtt broker (here: moquitto on local network)
# 2) publish to emoncms via get(url), also taking care of timeouts / exceptions
#
# Assumptions:
# - JNode micro TNode data structure
# - sending to YunHub 1.03 MQTT
#

STARTUP_MESSAGE_VERSION = '150411 mqtt_to_emoncms 1.05 beta'

import StringIO
import csv
import paho.mqtt.client as mqtt
import requests

from mytokens import EMONCMS_WRITE_API_KEY

emoncms_url_init = 'http://emoncms.org/input/post.json?apikey=' + EMONCMS_WRITE_API_KEY


# The callback for when the client receives a CONNACK response from the server.
def on_connect(mqttc, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqttc.subscribe("TNode", 0)


def on_disconnect(mqttc, obj, flags, rc):
    print('!!! mqtt disconnected, rc: ' + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    x = StringIO.StringIO(msg.payload)
    reader = csv.reader(x, delimiter=',')
    for datarow in reader:
        TNodeData = dict(date=datarow[0], group=datarow[1], node=datarow[2], Vcc=datarow[3], T_in=datarow[4],
                         T_out=datarow[5])

    # construct URL
    emoncms_url = emoncms_url_init + '&node=' + TNodeData['node'] + '&csv=' + TNodeData['Vcc'] + ',' + TNodeData[
        'T_in'] + ',' + TNodeData['T_out']
    print emoncms_url

    # send data to emoncms & handle exceptions.
    # Use requests instead of urllib2 to catch exceptions.
    try:
        response = requests.get(emoncms_url, timeout=1)
    except requests.ConnectionError as e:
        print e
        response = 'ConnectionError exception: No response'
    except:
        response = 'Unidentified exception ...'

    print response
    print


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_unsubscribe(mqttc, obj, mid, granted_qos):
    print("!!! Unsubscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


# If you want to use a specific client id, use mqttc = mqtt.Client("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe

# Uncomment to enable debug messages
# mqttc.on_log = on_log

print '###'
print '###'
print '### ' + STARTUP_MESSAGE_VERSION
print '###'
print '###'
print

# connect to mqtt server. Subscription takes place in on_connect.
# Timeout interval 60s. retry_first_connection=True
mqttc.connect("192.168.1.12", 1883, 60)
mqttc.loop_forever(retry_first_connection=True)