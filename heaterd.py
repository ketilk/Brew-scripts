#!/usr/bin/python

from Atlas.atlas import AtlasDaemon
from Atlas.topic import Topic
from Interfaces.bbio import OutputPin
import time

class Heater(object):
  def __init__(self, name, pin, period=300, power=0):
    self.name = name
    self.pin = pin
    self.power = power
    self.period = period
    self.thread = Thread(target=self._run)
    self.thread.setDaemon()
    self.thread.start()
  
  def update_power(self, power):
    self.power = power
  
  def _run(self):
    t0 = 0
    while True:
      if self.power <= 0:
        if self.pin.get_state():
          self.pin.set_low()
      elif t0 + self.period < time.time():
        t0 = time.time()
        self.pin.set_high()
      elif t0 + self.power * self.period < time.time():
        if self.pin.get_state():
          self.pin.set_low()
      time.sleep(0.1)
  
class HeaterDaemon(AtlasDaemon):
  
  def _init(self):
    
    if not self.configuration.has_section('Heaters'):
      self.logger.warning('Cannot find \"Heaters\" section.')
      return False
    
    self.period = 300
    self.heaters = []
    self.subscribers = []
    self.publishers = []
    
    for option in self.configuration.options('Heaters'):
      if option == 'period':
        self.period = float(self.configuration.get('Heaters', option))
      else:
        pin = OutputPin(self.configuration.get('Heaters', option))
        heater = Heater(option, pin, self.period)
        heaters.append(heater)
        subscriber = self.atlas.get_suscriber()
        topic = Topic('power', option, heater.power)
        self.publishers
    return True
    
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
  daemon = HeaterDaemon('/var/run/' + file_name + '.pid')
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