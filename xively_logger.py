#!/usr/bin/python

import signal
import sys
import os

from daemon import Daemon
from Atlas.atlas import *
from Atlas.topic import *
import xively
import time
import datetime
import requests

import logging

FEED_ID = '1620077696'
API_KEY = '71cG08OmuBBUJb13HdzO2sDCCE4zCDelFxYgPNvYm0IePRox'
file_name = os.path.basename(__file__)

xively_api = xively.XivelyAPIClient(API_KEY)

class XivelyLoggerDaemon(Daemon):
  def run(self):
    logging.basicConfig(filename=file_name + '.log',
      filemode='a',
      format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
      datefmt='%H:%M:%S',
      level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    subscriber_stream_tuplets = []
    feed = xively_api.feeds.get(FEED_ID)
  
    with Atlas() as atlas:
      subscriber_stream_tuplets.append(get_subscriber_stream_tuplet(
        atlas, feed, 'temperature', 'ferm1_sensor1', logger
      ))
      subscriber_stream_tuplets.append(get_subscriber_stream_tuplet(
        atlas, feed, 'temperature', 'ferm1_sensor2', logger
      ))
      subscriber_stream_tuplets.append(get_subscriber_stream_tuplet(
        atlas, feed, 'temperature', 'ferm1_sensor3', logger
      ))
      while True:
        for tuplet in subscriber_stream_tuplets:
          tuplet[1].current_value = tuplet[0].topic.payload
          tuplet[1].at = datetime.datetime.utcnow()
          try:
            tuplet[1].update()
          except requests.HTTPError as e:
            logger.warning('HTTPError({0}): {1}'.format(e.errno, e.strerror))
        time.sleep(5)
        
def get_subscriber_stream_tuplet(atlas, feed, topic_name, key, logger):
  topic = TopicDescription(topic_name, key)
  loop = True
  while loop:
    try:
      subscriber = atlas.get_subscriber(topic)
    except AtlasError:
      logger.warning('Could not get subscriber on topic: '
                      + str(topic) + '. Sleeping 3 seconds.')
      time.sleep(3)
    else:
      logger.info('Subscriber up on topic ' + str(topic))
      loop = False
  loop = True
  while loop:
    try:
      data_stream = feed.datastreams.get(key)
    except:
      logger.warning('Could not get data stream on key: '
                      + key + '. Sleeping 3 seconds')
      time.sleep(3)
    else:
      logger.info('Data stream established on key: ' + key + '.')
      loop = False
  return (subscriber, data_stream)
  
if __name__ == '__main__':
  daemon = XivelyLoggerDaemon('/tmp/xively_logger.pid')
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