#!/usr/bin/python

import signal
import sys

from Interfaces.ds18b20 import DS18B20
from Atlas.atlas import Atlas
from Atlas.topic import *

import logging

def main():
  logging.basicConfig(filename=__name__ + '.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)
  
  sensor_publisher_tuplets = []
  
  with Atlas() as atlas:
    sensor = DS18B20('28-000004f10b89')
    temp = sensor.get_temperature()
    topic = Topic(TopicDescription('temperature', 'ferm1_sensor1'), temp)
    publisher = atlas.get_publisher(topic)
    sensor_publisher_tuplets.append((sensor, publisher))
    sensor = DS18B20('28-000004f1f9bf')
    temp = sensor.get_temperature()
    topic = Topic(TopicDescription('temperature', 'ferm1_sensor2'), temp)
    publisher = atlas.get_publisher(topic)
    sensor_publisher_tuplets.append((sensor, publisher))
    sensor = DS18B20('28-00000522683f')
    temp = sensor.get_temperature()
    topic = Topic(TopicDescription('temperature', 'ferm1_sensor3'), temp)
    publisher = atlas.get_publisher(topic)
    sensor_publisher_tuplets.append((sensor, publisher))
    
    while True:
      for tuplet in sensor_publisher_tuplets:
        tuplet[1].publish(tuplet[0].get_temperature())
      time.sleep(1)

def signal_handler(signal, frame):
  sys.exit(0)
  
if __name__ == '__main__':
  signal.signal(signal.SIGINT, signal_handler)
  main()