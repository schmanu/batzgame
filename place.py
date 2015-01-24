import yaml

class Place(yaml.YAMLObject):
  """"
  		Class used for Places. Each place/setting in the game is an instance of this class.
  		Currently no magic happens here.
  """
  yaml_tag = u'!Place'

  def __init__(self, name, description, objects):
    super(Place, self).__init__()
    self.name = name
    self.description = description
    self.objects = objects

  def examine(self):
    return self.description
