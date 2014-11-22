from Interfaces.bbio import OutputPin
import time
from threading import Thread


class PWM(object):
    def __init__(pin, p=300, dc=1):
        self.pin = pin
        self.period = p
        self.dutycycle = dc
        self.thread = Thread(target=self._run)
        self.thread.setDaemon()
        self.thread.start()

    def _run(self):
        t0 = 0
        while True:
            if self.dutycycle <= 0:
                if self.pin.get_state():
                    self.pin.set_low()
            elif t0 + self.period < time.time():
                t0 = time.time()
                self.pin.set_high()
            elif t0 + self.dutycycle * self.period < time.time():
                if self.pin.get_state():
                    self.pin.set_low()
            time.sleep(0.1)