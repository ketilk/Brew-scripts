#!/usr/bin/python

from Atlas.atlas import AtlasDaemon
from Atlas.topic import Topic
from Interfaces.bbio import OutputPin
from threading import Thread
import time

class Heater(object):
  def __init__(self, pin, subscriber, period=300):
    self.pin = pin
    self.subscriber = subscriber
    self.power = 0
    self.period = period
    self.control_thread = Thread(target=self._run)
    self.control_thread.setDaemon()
    self.control_thread.start()
    self.power_thread = Thread(target=self._power)
    self.power_thread.setDaemon()
    self.power_thread.start()
  
  def get_power(self):
    return self.power
  
  def get_state(self):
    return self.pin.get_state()
  
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
      time.sleep(1)
  
  def _power(self):
    while True:
      power = self.subscriber.get_data(60)
      if power:
        self.power = power
      else:
        power = 0
  
class HeaterDaemon(AtlasDaemon):
  
  def _init(self):
    
    if not self.configuration.has_section('Heaters'):
      self.logger.warning('Cannot find \"Heaters\" section.')
      return False
    
    self.period = None
    self.pub_heater_tuplets = []
    
    for option in self.configuration.options('Heaters'):
      if option == 'period':
        self.period = float(self.configuration.get('Heaters', option))
      else:
        pin = OutputPin(self.configuration.get('Heaters', option))
        subscriber = self.get_subscriber('heater power', 'controller.' + option)
        heater = Heater(pin, subscriber, self.period)
        publisher1 = self.get_publisher('heater power', option)
        publisher2 = self.get_publisher('state', option)
        self.pub_heater_tuplets.append((publisher1, publisher2, heater))
    return True
    
  def _loop(self):
    for pub_heater_tuplet in self.pub_heater_tuplets:
      pub_heater_tuplet[0].publish(pub_heater_tuplet[2].get_power())
      pub_heater_tuplet[1].publish(pub_heater_tuplet[2].get_state())
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