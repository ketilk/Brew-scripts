#!/usr/bin/python

from Interfaces.ds18b20 import DS18B20
from Atlas.atlas import AtlasDaemon
from Atlas.topic import Topic
import time

class TemperatureDaemon(AtlasDaemon):
  
  def _init(self):
    self.sensors = []
    
    for key in self.configuration['DS18B20 Sensors']:
      sensor_id = self.configuration['DS18B20 Sensors'][key]
      sensor = DS18B20(sensor_id)
      topic = Topic('temperature', key, sensor.get_temperature())
      publisher = self.get_publisher(topic)
      self.sensors.append((sensor, publisher))
      self.logger.info('DS18B20 Sensors sensor instantiated: ' 
                        + key + ', ' + sensor_id)
    
    """sensor = DS18B20('28-000004f10b89')
    topic = Topic('temperature', 'sensor1', sensor.get_temperature())
    publisher = self.get_publisher(topic)
    self.sensors.append((sensor, publisher))
    
    sensor = DS18B20('28-000004f1f9bf')
    topic = Topic('temperature', 'sensor2', sensor.get_temperature())
    publisher = self.get_publisher(topic)
    self.sensors.append((sensor, publisher))
    
    sensor = DS18B20('28-00000522683f')
    topic = Topic('temperature', 'sensor3', sensor.get_temperature())
    publisher = self.get_publisher(topic)
    self.sensors.append((sensor, publisher))"""
    
  def _loop(self):
    for sensor in self.sensors:
      sensor[1].publish(sensor[0].get_temperature())
    time.sleep(1)

import logging
import sys
import os

file_name = os.path.splitext(os.path.basename(__file__))[0]
  
if __name__ == '__main__':
  logging.basicConfig(filename='/var/log/' + file_name + '.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)
  logger = logging.getLogger(__name__)
  daemon = TemperatureDaemon('/var/run/' + file_name + '.pid')
  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      daemon.start()
    elif 'stop' == sys.argv[1]:
      daemon.stop()
    elif 'restart' == sys.argv[1]:
      daemon.restart()
    else:
      print "Unknown command"
      sys.exit(2)
    sys.exit(0)
  else:
    print "usage: %s start|stop|restart" % sys.argv[0]
    sys.exit(2)