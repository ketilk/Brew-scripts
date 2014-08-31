class Average(object):
  def __init__(self, n=5, value):
    self.n = n
    self.values = []
    self.values.append(value)

  def set_value(self, value):
    if len(self.values) == self.n:
      self.values.pop(0)
      
    self.values.append(value)

  def get_value(self):
    sorted_list = sorted(self.values)
    
    if 3 <= len(self.values):
      sorted_list.pop(0)
      sorted_list.pop()
    
    return sum(sorted_list)/len(sorted_list)