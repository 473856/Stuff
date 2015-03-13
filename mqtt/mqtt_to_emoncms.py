#!/usr/bin/python

#
# 1) Read TNode data from mqtt broker (here: moquitto on local network)
# 2) publish to emoncms via get(url), also taking care of timeouts / exceptions
#
# Assumptions:
# - JNode micro TNode data structure
# - sending to YunHub 1.03 MQTT
#
# 150313 mqtt_to_emoncms 1.01
#

import StringIO
import csv
import paho.mqtt.client as mqtt
import requests

from mytokens import EMONCMS_WRITE_API_KEY

emoncms_url_init = 'http://emoncms.org/input/post.json?apikey=' + EMONCMS_WRITE_API_KEY


def on_connect(mqttc, obj, flags, rc):
    print('mqtt connect established, rc: ' + str(rc))


def on_disconnect(mqttc, obj, flags, rc):
    print('mqtt disconnected!, rc: ' + str(rc))


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

    # send data to emoncms, incl. error handling.
    # Use requests instead of urllib2 to catch [Errno 54] Connection reset by peer
    try:
        response = requests.get(emoncms_url, timeout=1)
    except requests.ConnectionError as e:  # This is the correct syntax
        print e
        response = 'No response'
    except:
        response = 'Unidentified exception ...'

    print response
    print


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)

# If you want to use a specific client id, use
# mqttc = mqtt.Client("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Uncomment to enable debug messages
# mqttc.on_log = on_log

print '###'
print '### mqtt_to_emoncms v1.0 150304'
print '###'
mqttc.connect("192.168.1.12", 1883, 60)
mqttc.subscribe("TNode", 0)

mqttc.loop_forever()