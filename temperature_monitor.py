#!/usr/bin/python

from Interfaces.ds18b20 import DS18B20
from Atlas.atlas import AtlasDaemon
from Atlas.topic import Topic

class TemperatureMonitorDaemon(AtlasDaemon):
  
  def _init(self):
    self.sensor = DS18B20('28-000004f10b89')
    temp = self.sensor.get_temperature()
    self.topic = Topic('temperature', 'ferm1', temp)
    self.publisher = self.get_publisher(self.topic)
    
  def _loop(self):
    self.topic.data = self.sensor.get_temperature()
    self.publisher.publish(self.topic)
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
    level=logging.DEBUG)
  logger = logging.getLogger(__name__)
  daemon = TemperatureMonitorDaemon('/var/run/' + file_name + '.pid')
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