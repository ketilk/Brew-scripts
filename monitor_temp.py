#!/usr/bin/python

from Interfaces.ds18b20 import DS18B20
from Atlas.atlas import Atlas
from Atlas.topic import *

def main():
  logging.basicConfig(filename='case2.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)
    
  sensors = []
  sensors.append(DS18B20('28-000004f10b89'))
  sensors.append(DS18B20('28-000004f1f9bf'))
  sensors.append(DS18B20('28-00000522683f'))
  
  publishers = []
  
  with Atlas() as atlas:
    temp = sensors[0].get_temperature()
    topic = Topic(TopicDescription('temperature', 'ferm1.1'), temp)
    publishers.append(atlas.get_publisher(topic))
    temp = sensors[1].get_temperature()
    topic = Topic(TopicDescription('temperature', 'ferm1.2'), temp)
    publishers.append(atlas.get_publisher(topic))
    temp = sensors[2].get_temperature()
    topic = Topic(TopicDescription('temperature', 'ferm1.3'), temp)
    publishers.append(atlas.get_publisher(topic))
    
    while True:
      for i in range(0, 3):
        publishers[i].publish(sensors[i].get_temperature())
      time.sleep(1)
  
if __name__ == '__main__':
  main()