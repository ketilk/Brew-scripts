#!/usr/bin/env python

from Atlas.atlas import Atlas
import logging
import time

def topic_handler(topic):
  print topic

logging.basicConfig(filename="tail.log",
  filemode='a',
  format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
  datefmt='%H:%M:%S',
  level=logging.DEBUG)
logger = logging.getLogger
    
atlas = Atlas()
atlas.register_topic_handler(topic_handler)


while True:
  try:
    time.sleep(1)
  except:
    break
