#!/usr/bin/python

import logging
import time

from daemon import runner

class App(object):
  
  def __init__(self):
    self.stdin_path = '/dev/null'
    self.stdout_path = '/dev/tty'
    self.stderr_path = '/dev/tty'
    self.pidfile_path =  '/var/run/daemon_test.pid'
    self.pidfile_timeout = 5
    
  def run(self):
    while True:
      #Main code goes here ...
      #Note that logger level needs to be set to logging.DEBUG before this shows up in the logs
      logger.debug("Debug message")
      logger.info("Info message")
      logger.warn("Warning message")
      logger.error("Error message")
      time.sleep(10)
      
if __name__ == '__main__':
  app = App()
  logger = logging.getLogger("DaemonLog")
  logger.setLevel(logging.INFO)
  formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  handler = logging.FileHandler("/var/log/daemon_test.log")
  handler.setFormatter(formatter)
  logger.addHandler(handler)

  daemon_runner = runner.DaemonRunner(app)
  #This ensures that the logger file handle does not get closed during daemonization
  daemon_runner.daemon_context.files_preserve=[handler.stream]
  daemon_runner.do_action()