#!/usr/bin/python

from Atlas.atlas import AtlasDaemon
from Atlas.topic import Topic

class ControllerDaemon(AtlasDaemon):
  
  def _init(self):
    if not self.configuration.has_section('Controller'):
      self.logger.warning('Cannot find \"Heaters\" section.')
      return False
    self.targets = []
    
    for option in self.configuration.options('Controller'):
      try:
        target_temp = float(self.configuration.get('Controller', option))
      except ValueError:
        target_temp = None
      self.targets.append((option, target_temp))
    
  def _loop(self):
    pass
  
  def _end(self):
    pass

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