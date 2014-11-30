#!/usr/bin/python

from Atlas.atlas import AtlasDaemon
from Atlas.topic import Topic
from Interfaces.bbio import OutputPin
from threading import Thread
from Atlas.subscriber import SubscriberTimeout
import time


class Heater(object):
    def __init__(self, pin, max_power, period):
        self.logger = logging.getLogger(__name__)
        self.pin = pin
        self.max_power = max_power
        self.power_set = 0
        self.power = 0
        self.period = period
        self.control_thread = Thread(target=self._run)
        self.control_thread.setDaemon(True)
        self.control_thread.start()

    def get_power(self):
        return self.power

    def set_power(self, power):
        self.logger.debug('Setting heater power.')
        if not isinstance(power, float):
            self.pin.set_low()
            raise TypeError()
        self.power_set = time.time()
        if self.max_power < power:
            self.power = self.max_power
        else:
            self.power = power
        self.logger.debug('Heater power was set: ' + str(power))

    def get_state(self):
        return self.pin.get_state()

    def _run(self):
        t0 = 0
        while True:
            if self.power_set + 0.25 * self.period < time.time():
                self.logger.debug('Didn\'t receive power update. resetting power.')
                self.power = 0
            power_fraction = self.power / self.max_power
            self.logger.debug('Power fraction: ' + str(power_fraction))
            if self.power <= 0:
                self.logger.debug('Zero or negative power, setting pin low.')
                if self.pin.get_state():
                    self.pin.set_low()
            elif t0 + self.period < time.time():
                self.logger.debug('Resetting time and setting pin high.')
                t0 = time.time()
                self.pin.set_high()
            elif t0 + power_fraction * self.period < time.time():
                self.logger.debug('Time to set pin low.')
                if self.pin.get_state():
                    self.pin.set_low()
            time.sleep(1)


class HeaterDaemon(AtlasDaemon):
    def _init(self):

        if not self.configuration.has_section('Heaters'):
            self.logger.warning('Cannot find \"Heaters\" section.')
            return False

        period = 300
        self.tuplets = []

        for option in self.configuration.options('Heaters'):
            if option == 'period':
                period = float(self.configuration.get('Heaters', option))
            else:
                arguments = self.configuration.get('Heaters', option).split(',')
                pin = OutputPin(arguments[0])
                max_power = float(arguments[1])
                subscriber = self.get_subscriber('power', 'controller.' + option)
                heater = Heater(pin, max_power, period)
                power_publisher = self.get_publisher('power', option)
                state_publisher = self.get_publisher('state', option)
                self.tuplets.append((subscriber, heater, power_publisher, state_publisher))
        return True

    def _loop(self):
        for tuplet in self.tuplets:
            subscriber, heater, power_publisher, state_publisher = tuplet
            try:
                power = subscriber.get_data(0.05)
            except SubscriberTimeout:
                self.logger.debug('No new data available')
            else:
                self.logger.debug('Setting heater power: ' + str(power))
                if isinstance(power, float):
                    heater.set_power(power)
            finally:
                power_publisher.publish(heater.get_power())
                state_publisher.publish(heater.get_state())
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