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
    self.t_cycle = self.t0
    self.cycle_period = 5 * 60 #5 minutes
    self.power = 0.2 #20% of full power
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
    
    topic = Topic("state", "heater", self.pin.get_state())
    self.heater_publisher = self.get_publisher(topic)
    
    topic = Topic("stage", "calibration_stage", 1)
    self.stage_publisher = self.get_publisher(topic)

  def _loop(self):
    if time.time() < self.t0 + self.stage1:
      if self.pin.get_state():
        self.pin.set_low()
      self.stage_publisher.publish(1)
    elif time.time() < self.t.0 + self.stage1 + self.stage2:
      self.stage_publisher.publish(2)
      if self.t_cycle + self.cycle_period < time.time():
        self.t_cycle = time.time()
        self.pin.set_high()
      elif self.t_cycle + self.power * self.cycle < time.time():
        self.pin.set_low()
    elif self.t.0 + self.stage1 + self.stage2 < time.time():
      if self.pin.get_state():
        self.pin.set_low()
      self.stage_publisher.publish(3)
    
    for triple in self.triplets:
      triple[1].update(triple[0].topic.data)
      triple[2].publish(triple[1].get_value())
    self.heater_publisher.publish(self.pin.get_state())
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