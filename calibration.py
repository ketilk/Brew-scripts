#!/usr/bin/python

import sys
import os
import time
import logging

from average import Average
from Atlas.atlas import AtlasDaemon, AtlasError
from Atlas.topic import Topic
from Interfaces.bbio import OutputPin

class CalibrationDaemon(AtlasDaemon):
  def _init(self):
    self.pin = OutputPin("P8_10")
    self.pin.set_low()
    self.t0 = time.time()
    self.stage1 = 6 * 60 * 60 #6 hours
    self.stage2 = 6 * 60 * 60 #6 hours
    self.stage3 = 6 * 60 * 60 #6 hours
    self.triplets = []
    
    subscriber = self.get_subscriber(Topic("temperature", "sensor1"))
    average_temp = Average(subscriber.topic.data, 10)
    topic = Topic("temperature", "sensor1_average", average_temp.get_value())
    publisher = self.get_publisher(topic)
    self.triplets.append((subscriber, average_temp, publisher))
    
    subscriber = self.get_subscriber(Topic("temperature", "sensor2"))
    average_temp = Average(subscriber.topic.data, 10)
    topic = Topic("temperature", "sensor2_average", average_temp.get_value())
    publisher = self.get_publisher(topic)
    self.triplets.append((subscriber, average_temp, publisher))
    
    subscriber = self.get_subscriber(Topic("temperature", "sensor3"))
    average_temp = Average(subscriber.topic.data, 10)
    topic = Topic("temperature", "sensor3_average", average_temp.get_value())
    publisher = self.get_publisher(topic)
    self.triplets.append((subscriber, average_temp, publisher))

  def _loop(self):
    for triple in self.triplets:
      triple[1].update(triple[0].topic.data)
      triple[2].publish(triple[1].get_value())
    time.sleep(1)

if __name__ == '__main__':
  file_name = os.path.splitext(os.path.basename(__file__))[0]
  logging.basicConfig(filename='/var/log/' + file_name + '.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)
  daemon = CalibrationDaemon('/var/run/' + file_name + '.pid')
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