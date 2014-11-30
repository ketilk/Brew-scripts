#!/usr/bin/python

from Atlas.atlas import AtlasDaemon
from Atlas.subscriber import SubscriberTimeout
import time
from math import sqrt
from average import Average


class Controller(object):
    def __init__(self):
        self.power = 0.0

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
        self.mu = 2.0 * (sqrt(1 + self.gain) - self.delta)
        self.etta = 0.9 * (1 + self.gain) * (2.0 * self.delta + self.mu)
        self.points = []
        self.error = 0.0
        self.derivator = 0.0
        self.integrator = 0.0

    def update(self, t_o):
        if not isinstance(t_o, float):
            raise TypeError()
        self.points.append((time.time(), t_o))
        self.points = self._relevant_points()
        self.error = self.set_point - t_o
        try:
            self._derivator()
            self._integrator()
        except LookupError:
            self.power = 0.0
        else:
            self.power = (self.gain / self.r_o * self.error +
                          self.mu / self.omega_n / self.r_o * self.derivator +
                          self.etta * self.omega_n / self.r_o * self.integrator)

    def set_point(self, set_point):
        self.set_point = set_point

    def _relevant_points(self):
        relevant_points = [point for point in self.points if time.time() - point[0] < self.period]
        return relevant_points

    def _derivator(self):
        if 1 < len(self.points):
            t1, t_o1 = self.points[0]
            t2, t_o2 = self.points[-1]
            self.derivator = (t_o2 - t_o1) / (t2 - t1)
        else:
            raise LookupError()

    def _integrator(self):
        if 1 < len(self.points):
            deltoids = []
            for index, elem in enumerate(self.points[1:]):
                t1, t_o1 = self.points[index - 1]
                t2, t_o2 = elem
                integrand1 = self.set_point - t_o1
                integrand2 = self.set_point - t_o2
                da = (integrand1 + integrand2) / 2 * (t2 - t1)
                deltoids.append(da)
            self.integrator = sum(deltoids)
        else:
            raise LookupError()


class Calibrator(Controller):
    def __init__(self, power):
        super(Calibrator, self).__init__()
        if not isinstance(power, float):
            raise TypeError()
        self.power = power


class ControllerDaemon(AtlasDaemon):
    def _init(self):
        if not self.configuration.has_section('Controllers'):
            self.logger.error('Cannot find \"Controllers\" section.')
            return False

        self.tuplets = []
        self.algorithms = []
        period = 300

        subscriber = self.get_subscriber('temperature', 'sensor2')
        average = Average(10)
        average_pub = self.get_publisher('temperature', 'average.sensor2')
        self.algorithms.append((subscriber, average, average_pub))

        for option in self.configuration.options('Controllers'):
            arguments = self.configuration.get('Controllers', option).split(',')
            heater_id = arguments[0]
            controller_pub = self.get_publisher('power', 'controller.' + heater_id)
            if arguments[1] == 'calibrate':
                controller = Calibrator(float(arguments[2]))
                temp_sub = None

            else:
                try:
                    set_point = float(arguments[1])
                    sensor_id = arguments[2]
                    gain = float(arguments[3])
                    c_h = float(arguments[4])
                    r_ho = float(arguments[5])
                    c_o = float(arguments[6])
                    r_o = float(arguments[7])
                except ValueError:
                    self.logger.error('Error in reading configuration  for ' + option)
                    return False
                else:
                    setpoint_pub = self.get_publisher('temperature', 'controller.setpoint')
                    temp_sub = self.get_subscriber('temperature', sensor_id)
                    controller = PIDController(set_point, period, gain, c_h, r_ho, c_o, r_o)
            tuplet = (temp_sub, controller, controller_pub, setpoint_pub)
            self.tuplets.append(tuplet)
        return True

    def _loop(self):
        self.logger.debug('Looping........')
        for algorithm in self.algorithms:
            subscriber, average, average_pub = algorithm
            average.update(subscriber.get_data())
            try:
                av = average.get_value()
            except ArithmeticError:
                self.logger.debug('Arithmetic error detected.')
            else:
                average_pub.publish(av)

        for tuplet in self.tuplets:
            temp_sub, controller, controller_pub, setpoint_pub = tuplet
            if temp_sub:
                try:
                    controller.update(temp_sub.get_data(.05))
                except SubscriberTimeout:
                    self.logger.debug('No data available for controller.')
            controller_pub.publish(controller.power)
            setpoint_pub.publish(controller.set_point)
        time.sleep(1)

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