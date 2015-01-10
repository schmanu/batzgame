import yaml

class Place(yaml.YAMLObject):
  """docstring for Place"""
  yaml_tag = u'!Place'

  def __init__(self, name, description, objects):
    super(Place, self).__init__()
    self.name = name
    self.description = description
    self.objects = objects

  def examine(self):
    return self.description
