import math


class Average(object):
    def __init__(self, n=5):
        self.n = n
        self.values = []

    def update(self, value):
        self.values.append(value)
        if len(self.values) == self.n + 1:
            self.values.pop(0)

    def get_value(self):
        if len(self.values) == self.n:
            sorted_list = sorted(self.values)
            n = int(math.ceil(self.n / 3))
            return sum(sorted_list[n:-n]) / (self.n - 2 * n)
        else:
            raise ArithmeticError()