#!/usr/bin/python

# Copyright (c) 2010-2013 Roger Light <roger@atchoo.org>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution. 
#
# The Eclipse Distribution License is available at 
# http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
# Roger Light - initial implementation
# Copyright (c) 2010,2011 Roger Light <roger@atchoo.org>
# All rights reserved.

# This shows a simple example of an MQTT subscriber.

import StringIO
import csv

import paho.mqtt.client as mqtt
import urllib2

from mytokens import EMONCMS_WRITE_API_KEY

emoncms_url_init = 'http://emoncms.org/input/post.json?apikey=' + EMONCMS_WRITE_API_KEY


def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


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

    # send data to emoncms, incl. error handling
    request = urllib2.Request(emoncms_url)
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        print('HTTPError = ' + str(e.code))
    except urllib2.URLError, e:
        print('URLError = ' + str(e.reason))
    except httplib.HTTPException, e:
        print('HTTPException')
    except Exception:
        import traceback

        print('generic exception: ' + traceback.format_exc())


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
mqttc.connect("192.168.1.12", 1883, 60)
mqttc.subscribe("TNode", 0)

mqttc.loop_forever()