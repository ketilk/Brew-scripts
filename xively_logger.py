#!/usr/bin/python

from Atlas.atlas import *
from Atlas.topic import *
import xively

import logging

FEED_ID = '1620077696'
API_KEY = '71cG08OmuBBUJb13HdzO2sDCCE4zCDelFxYgPNvYm0IePRox'

def main():
  logging.basicConfig(filename='xively_logger.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)
    
    subscriber_stream_tuplets = []
    
    with Atlas() as atlas:
      topic = TopicDescription('temperature', 'ferm1.sensor1')
      subscriber = atlas.get_subscriber