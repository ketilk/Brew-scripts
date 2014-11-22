#!/usr/bin/python

import MySQLdb as mdb
import sys

try:
    con = None
    con = mdb.connect('localhost', 'brewscript', 'brew101', 'BrewingDB');
    cur = con.cursor()
    cur.execute("SELECT VERSION()")

    ver = cur.fetchone()

    print "Database version : %s " % ver

    cur.execute("DROP TABLE IF EXISTS TEMPERATURE_TBL")
    cur.execute("CREATE TABLE TEMPERATURE_TBL(\
              TMP_ID INT PRIMARY KEY AUTO_INCREMENT,\
              TMP_KEY VARCHAR(25),\
              TMP_TIME FLOAT(16),\
              TMP_VAL FLOAT(16))")
    cur.execute("DROP TABLE IF EXISTS POWER_TBL")
    cur.execute("CREATE TABLE POWER_TBL(\
              PWR_ID INT PRIMARY KEY AUTO_INCREMENT,\
              PWR_KEY VARCHAR(25),\
              PWR_TIME FLOAT(16),\
              PWR_VAL FLOAT(16))")
    cur.execute("DROP TABLE IF EXISTS STATE_TBL")
    cur.execute("CREATE TABLE STATE_TBL(\
              STE_ID INT PRIMARY KEY AUTO_INCREMENT,\
              STE_KEY VARCHAR(25),\
              STE_TIME FLOAT(16),\
              STE_VAL INTEGER)")
except mdb.Error, e:

    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

finally:

    if con:
        con.close()