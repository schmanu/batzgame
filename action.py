import yaml
class Action(yaml.YAMLObject):
  """docstring for Action"""
  yaml_tag = u'!Action'
  def __init__(self, operation, target, target2, text, changes, conditions):
    super(Action, self).__init__()
    self.operation = operation
    self.target = target
    self.target2 = target2
    self.conditions = conditions
    self.changes = changes
    self.text = text
    