#!/usr/bin/env python

from Atlas.atlas import Atlas
import logging
import time

logging.basicConfig(filename="tail.log",
  filemode='a',
  format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
  datefmt='%H:%M:%S',
  level=logging.DEBUG)
logger = logging.getLogger
    
atlas = Atlas()

while True:
  try:
    print atlas.get_topic()
  except:
    break
