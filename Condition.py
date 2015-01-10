
class Condition(object):
  """docstring for Condition"""


  def checkCondition(self):
    return false



class ObjectCondition(Condition):
  """docstring for ObjectCondition"""
  def __init__(self, obj, check):
    super(Condition).__init__()
    self.obj = obj
    self.check = check

  def checkCondition(self):
    checker = getattr(self.obj, self.check)
    return checker()    
    

class PlaceCondition(Condition):
  """docstring for ObjectCondition"""
  def __init__(self, place, game):
    super(Condition).__init__()
    self.place = plae
    self.game = game

  def checkCondition(self):
    checker = getattr(self.obj, self.check)
    return checker()      
    