import yaml
from game import State
class Item(yaml.YAMLObject):
  """docstring for Item"""
  yaml_tag = u'!Item'

  def __init__(self, name, description, active, belongs_to):
    super(Item, self).__init__()
    self.name = name
    self.description = description
    self.belongs_to = belongs_to
    self.active = active


  def __str__(self):
    return "name: "+self.name+"\ndescription: "+self.description

  def __repr__(self):
    return self.name

  def examine(self):
    return self.description

  def activate(self):
    self.active = True

  def deactivate(self):
    self.active = False

  def destroy(self):
    self.deactivate()
    if self.name in State.inventory:
      State.inventory.remove(self.name)
    self.belongs_to = None

  def isDestroyed(self):
    return self.belongs_to == None and not self.active 

  def isActive(self):
    return self.active

  def isNotInInventory(self):
    return not (self.belongs_to == 'inventory')

  def isInInventory(self):
    return (self.belongs_to == 'inventory')

  def isAt(self, place):
    return (self.belongs_to == place)

  def putToPlace(self, place):
    if self.name in State.inventory:
      State.inventory.remove(self.name)
    self.belongs_to = place
    
  def toInventory(self):
    self.belongs_to = 'inventory'
    State.inventory.append(self.name)
