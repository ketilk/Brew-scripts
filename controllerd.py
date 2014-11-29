#!/usr/bin/python

from Atlas.atlas import AtlasDaemon
import time
from math import sqrt


class Controller(object):
    def __init__(self):
        self.power = 0

    def update(self, t_0):
        pass


class PIDController(Controller):
    def __init__(self, set_point, period, gain, c_h, r_ho, c_o, r_o):
        super(PIDController, self).__init__()
        self.set_point = set_point
        self.period = period
        self.gain = gain
        self.r_o = r_o
        self.omega_n = sqrt(1 / (c_h * r_ho * c_o * r_o))
        self.delta = self.omega_n / 2 * (c_o * r_o + c_h * r_o + c_h * r_ho)
        self.mu = 2 * (sqrt(1 + self.gain) - self.delta)
        self.etta = 0.9 * (1 + self.gain) * (2 * self.delta + self.mu)
        self.points = []

    def update(self, t_o):
        t = time.time()
        self.points.append((t, t_o))
        if self.period < t - self.points[0][0]:
            self.points.pop(0)
        error = self.set_point - t_o
        dt = self.points[-1][0] - self.points[0][0]
        dy = self.points[-1][1] - self.points[0][1]
        derivator = - dy / dt
        deltoids = []
        for index, elem in enumerate(self.points[1:]):
            dt = elem[0] - self.points[index - 1][0]
            deltoids.append(dt * elem[1])
        integrator = sum(deltoids)
        self.power = (self.gain / self.r_o * error +
                      self.mu / self.omega_n / self.r_o * derivator +
                      self.etta * self.omega_n / self.r_o * integrator)

    def set_point(self, set_point):
        self.set_point = set_point


class Calibrator(Controller):
    def __init__(self, power):
        super(Calibrator, self).__init__()
        self.power = power


class ControllerDaemon(AtlasDaemon):
    def _init(self):
        if not self.configuration.has_section('Controllers'):
            self.logger.error('Cannot find \"Controllers\" section.')
            return False
        self.tuplets = []

        for option in self.configuration.options('Controllers'):
            arguments = self.configuration.get('Controllers', option).string.split(',')
            heater_id = arguments[0]
            publisher = self.get_publisher('power', 'controller.' + heater_id)
            if arguments[1] == 'calibrate':
                controller = Calibrator(arguments[2])
                subscriber = None
            else:
                try:
                    set_point = float(arguments[1])
                    sensor_id = arguments[2]
                    gain = arguments[3]
                    c_h = arguments[4]
                    r_ho = arguments[5]
                    c_o = arguments[6]
                    r_o = arguments[7]
                except ValueError:
                    self.logger.error('Error in reading configuration  for ' + option)
                    return False
                subscriber = self.get_subscriber('temperature', sensor_id)
                controller = PIDController(set_point, period, gain, c_h, r_ho, c_o, r_o)

            self.tuplets.append((subscriber, controller, publisher))
        return True

    def _loop(self):
        for tuplet in self.tuplets:
            subscriber, controller, publisher = tuplet
            if subscriber:
                controller.update(subscriber.get_data())
            publisher.publish(controller.power)
        time.sleep(30)

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