#!/usr/bin/python

import MySQLdb as mdb
from Atlas.atlas import AtlasDaemon
from Atlas.topic import Topic

create_temperature_table = (
  "CREATE TABLE IF NOT EXISTS TEMPERATURE_TBL(\
  TMP_ID INT PRIMARY KEY AUTO_INCREMENT,\
  TMP_KEY VARCHAR(25),\
  TMP_TIME FLOAT(32),\
  TMP_VAL FLOAT(32))"
  )

create_power_table = (
  "CREATE TABLE IF NOT EXISTS POWER_TBL(\
  PWR_ID INT PRIMARY KEY AUTO_INCREMENT,\
  PWR_KEY VARCHAR(25),\
  PWR_TIME FLOAT(32),\
  PWR_VAL FLOAT(32))"
  )

create_state_table = (
  "CREATE TABLE IF NOT EXISTS STATE_TBL(\
  STE_ID INT PRIMARY KEY AUTO_INCREMENT,\
  STE_KEY VARCHAR(25),\
  STE_TIME FLOAT(32),\
  STE_VAL INTEGER)"
)

add_temperature = (
  "INSERT INTO TEMPERATURE_TBL(TMP_KEY, TMP_TIME, TMP_VAL) "
  "VALUES (%s, %s, %s)"
)

add_power = (
  "INSERT INTO POWER_TBL(PWR_KEY, PWR_TIME, PWR_VAL) "
  "VALUES (%s, %s, %s)"
)

add_state = (
  "INSERT INTO STATE_TBL(STE_KEY, STE_TIME, STE_VAL) "
  "VALUES (%s, %s, %s)"
)

def get_dat(topic):
  return (topic.key, float(topic.time), float(topic.data))

class PersistenceDaemon(AtlasDaemon):
  
  def _init(self):
    try:
      self.con = None
      self.con = mdb.connect('localhost', 'brewscript', 'brew101', 'BrewingDB');
      cursor = self.con.cursor()
      cursor.execute("SELECT VERSION()")

      ver = cursor.fetchone()
    
      print "Database version : %s " % ver
  
      cursor.execute(create_temperature_table)
      cursor.execute(create_power_table)
      cursor.execute(create_state_table)
      self.con.commit()
      cursor.close()
      
    except mdb.Error, e:
      msg = "Error %d: %s" % (e.args[0],e.args[1])
      self.logger.error(msg)
      return False

    self.logger.info("Persistence daemon initiated.")
    return True
    
  def _loop(self):
    self.logger.debug("Looping now...")
    topic = self.atlas.get_topic()
    self.logger.debug(topic)
    data = get_dat(topic)
    cursor = self.con.cursor()
    if topic.name == "temperature":
      self.logger.debug("Logging temperature:")
      self.logger.debug(data)
      self.logger.debug(type(data[0]))
      self.logger.debug(type(data[1]))
      self.logger.debug(type(data[2]))
      cursor.execute(add_temperature, data)
      self.logger.debug("Inserted temperature")
    elif topic.name == "power":
      self.logger.debug("Logging power:")
      self.logger.debug(data)
      self.logger.debug(type(data[0]))
      self.logger.debug(type(data[1]))
      self.logger.debug(type(data[2]))
      cursor.execute(add_power, data)
      self.logger.debug("Inserted power")
    elif topic.name == "state":
      self.logger.debug("Logging state:")
      self.logger.debug(data)
      self.logger.debug(type(data[0]))
      self.logger.debug(type(data[1]))
      self.logger.debug(type(data[2]))
      cursor.execute(add_state, data)
      self.logger.debug("Inserted state")
    self.con.commit()
    cursor.close()
  
  def _end(self):
    self.con.close()

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
  daemon = PersistenceDaemon('/var/run/' + file_name + '.pid')
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