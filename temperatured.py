#!/usr/bin/python

from Interfaces.ds18b20 import DS18B20
from Atlas.atlas import AtlasDaemon
from Atlas.topic import Topic
import time


class TemperatureDaemon(AtlasDaemon):
    def _init(self):
        self.sensors = []

        if not self.configuration.has_section('DS18B20 Sensors'):
            self.logger.warning('Cannot find \"DS18B20 Sensors\" section.')
            return False

        for option in self.configuration.options('DS18B20 Sensors'):
            sensor_id = self.configuration.get('DS18B20 Sensors', option)
            sensor = DS18B20(sensor_id)
            topic = Topic('temperature', option, sensor.get_temperature())
            publisher = self.get_publisher('temperature', option)
            self.sensors.append((sensor, publisher))
            self.logger.info('DS18B20 Sensors sensor instantiated: '
                             + option + ', ' + sensor_id)
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
    daemon = TemperatureDaemon('/var/run/' + file_name + '.pid')
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