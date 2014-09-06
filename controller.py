#!/usr/bin/python

import sys
import os
import logging
import time

from daemon import Daemon
from average import Average
from pid import PID
from Atlas.atlas import Atlas, AtlasError
from Atlas.topic import *
from Interfaces.bbio import OutputPin

file_name = os.path.splitext(os.path.basename(__file__))[0]

class ControllerState(object):
  init = 1
  off = 2
  on = 3

class ControllerDaemon(Daemon):
  
  def _init(self):
    logging.basicConfig(filename='/var/log/' + file_name + '.log',
      filemode='a',
      format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
      datefmt='%H:%M:%S',
      level=logging.INFO)
    self.logger = logging.getLogger(__name__)
    self.logger.info("=================Starting daemon==================")
  
    self.state = ControllerState.init
    self.period = 5 * 60
    self.pid = PID()
    self.pid.setPoint(19)
    self.update_time = 0
    self.pin = OutputPin("P8_10")
  
  def run(self):
    try:
      self._init()
    except:
      self.logger.exception("Caught exception during daemon init.")
    
    with Atlas() as self.atlas:
      self.logger.info("starting main loop.")
      while True:
        try:
          self._loop()
        except:
          self.logger.exception("Caught exception in daemon main thread.")
        time.sleep(5)
    
  def _loop(self):
    if self.state == ControllerState.init:
      try:
        self.subscriber = atlas.get_subscriber(TopicDescription("temperature", 
                                          "ferm1_sensor1"))
        self.temperature = Average(self.subscriber.topic.payload)
        pid = self.pid.update(self.temperature.get_value())
        topic = Topic(TopicDescription("pid", "ferm1_pid"), pid)
        self.publisher1 = atlas.get_publisher(topic)
        topic = Topic(TopicDescription("state", "ferm1_heating"), 0)
        self.publisher2 = atlas.get_publisher(topic)
        topic = Topic(TopicDescription("temperature", "ferm1_target"), 19)
        self.publisher3 = atlas.get_publisher(topic)
        topic = Topic(TopicDescription("temperature", "ferm1_sensor1_average"), 
                                        self.temperature.get_value())
        self.publisher4 = atlas.get_publisher(topic)
      except AtlasError:
        self.logger.debug("Error getting subscriber.")
        pass
      else:
        self.logger.info("Subscriber and publishers set up.")
        self.state = ControllerState.off
    
    elif self.state == ControllerState.off:
      temperature = self.temperature.set_value(self.subscriber.topic.payload)
      pid = self.pid.update(temperature)
      self.publisher1.publish(pid)
      self.publisher2.publish(0)
      self.publisher3.publish(19)
      self.publisher4.publish(temperature)
      if self.update_time + self.period < time.time():
        self.pin.set_high()
        self.update_time = time.time()
        self.state = ControllerState.on
    
    elif self.state == ControllerState.on:
      temperature = self.temperature.update(self.subscriber.topic.payload)
      pid = self.pid.update(temperature)
      self.publisher1.publish(pid)
      self.publisher2.publish(1)
      self.publisher3.publish(19)
      self.publisher4.publish(temperature)
      if self.update_time + pid * self.period < time.time():
        self.pin.set_low()
        self.state = ControllerState.off

if __name__ == '__main__':
  daemon = ControllerDaemon('/var/run/' + file_name + '.pid')
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