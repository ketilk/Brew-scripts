#!/usr/bin/python

import sys
import os
import time

from average import Average
from pid import PID
from Atlas.atlas import AtlasDaemon, AtlasError
from Atlas.topic import Topic
from Interfaces.bbio import OutputPin

class State(object):
  off = 0
  on = 1

class ControllerDaemon(AtlasDaemon):
  
  def _init(self):
    self.logger.info("Initializing controller daemon.")
    self.temp_target = 19
    self.update_time = 0
    self.period = 5 * 60
    self.duty_cycle = 0
    self.pid = PID()
    self.pid.setPoint(self.temp_target)
    self.pin = OutputPin("P8_10")
    self.heater = State.off
    
    self.subscriber = self.get_subscriber(Topic("temperature", "ferm1_wort"))
    self.wort_temp = Average(self.subscriber.get_topic())
    topic = Topic("temperature, ferm1_wort_average", self.wort_temp.get_value())
    self.publisher_average_temp = self.get_publisher(topic)
    topic = Topic("pid", "ferm1_pid", 
                  self.pid.update(self.wort_temp.get_value()))
    self.publisher_pid = self.get_publisher(topic)
    topic = Topic(TopicDescription("state", "ferm1_heating"), self.heater)
    self.publisher_heater = self.get_publisher(topic)
    topic = Topic(TopicDescription("temperature", "ferm1_target"), self.temp_target)
    self.publisher_target = self.get_publisher(topic)
    self.topic = Topic("percentage", "ferm1_duty_cycle", self.duty_cycle)
    self.publisher_duty_cycle = self.get_publisher(topic)
    
    self.logger.info("Controller initialized.")
    
  def _loop(self):
    self.wort_temp.update(self.subscriber.topic.data)
    self.publisher_average.publish(self.wort_temp.get_value())
    pid = self.pid.update(self.wort_temp.get_value())
    self.publisher_pid.publish(pid)
    self.publisher_target.publish(self.temp_target)
    if pid < 1:
      self.duty_cycle = pid
    else:
      self.duty_cycle = 1
    self.publisher_duty_cycle.publish(self.duty_cycle)
    
    if self.update_time + self.period < time.time():
      self.update_time = time.time()
      self.heater = State.on
      self.pin.set_high()
    elif self.update_time + self.duty_cycle < time.time():
      self.heater = State.off
      self.pin.set_low()
      
    self.publisher_heater.publish(self.heater)
    time.sleep(1)

if __name__ == '__main__':
  file_name = os.path.splitext(os.path.basename(__file__))[0]
  logging.basicConfig(filename='/var/log/' + file_name + '.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)
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