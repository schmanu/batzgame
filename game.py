import yaml, time, sys

class Game(object):
  """docstring for Game"""

  def __init__(self, loadfile = None):
    super(Game, self).__init__()
    stream = open("batzgame.yaml", 'r')
    gamedata = yaml.load(stream)
    self.objects = dict([ (o.name, o) for o in gamedata['objects'] ])
    self.title = gamedata['title']
    self.introduction = gamedata['introduction']
    self.places = dict([ (p.name , p) for p in gamedata['places'] ])
    self.startplace = self.places[gamedata['startplace']]

    self.actions = dict()
    for action in gamedata['actions']:
      self.addAction(action)
    State.inventory = gamedata['startinventory']
    if not loadfile:
      self.initNewGame()
    else:
      self.loadGame(loadfile)

  def loadGame(self, loadfile):
    stream = open(loadfile+".sav", 'r')
    gamedata = yaml.load(stream)
    self.objects = gamedata['objects']
    State.inventory = gamedata['inventory']
    self.changePlace(gamedata['currentplace'])

  def initNewGame(self):
    Game.animatedprint(self.introduction)
    #time.sleep(3)
    self.changePlace(self.startplace)

  def addAction(self, action):
    if hasattr(action, 'target2'):
      Game.addOrAppendToDict(self.actions, action.operation + action.target + ' ' + action.target2, action)
      Game.addOrAppendToDict(self.actions, action.operation + action.target2 + ' ' + action.target, action)
    else:
      Game.addOrAppendToDict(self.actions, action.operation + action.target, action)

  @staticmethod
  def addOrAppendToDict(d, key, newvalue):
    if key in d:
      oldvalue = d[key]
      if isinstance(oldvalue, list):
        oldvalue.append(newvalue)
        d[key] = oldvalue
      else:
        d[key] = list([oldvalue, newvalue])
    else:
      d[key] = newvalue

  def changePlace(self, where):
    State.currentplace = where
    Game.animatedprint(where.description)

  def examine(self, what):
    if what in self.objects:
        if self.objects[what].isActive():
          Game.animatedprint(self.objects[what].description)
          return
    Game.animatedprint("Ich kann "+what+" nicht finden.\n")

  def use(self, what):
    if not self.executeOperation(what, "benutze"):
      print("Nichts besonderes passiert.")

  def take(self, what):
    if what in self.objects:
      take_obj = self.objects[what]
      if take_obj.isActive() and take_obj.isNotInInventory() and take_obj.belongs_to == State.currentplace.name:
        if self.executeOperation(what, "nehme"):
          take_obj.toInventory()
          return
    print("Das kann ich nicht tun.")

  def go(self, where):
    if not self.executeOperation(where, "gehe"):
      print("Das kann ich nicht tun")
  def checkInventory(self):
    for item in State.inventory:
      print(item)

  def umsehen(self):
    print(State.currentplace.description)

  def executeOperation(self, what, operation):
    if operation+what in self.actions:
      actions = self.actions[operation+what]
      if not isinstance(actions, list):
        actions = list([actions])
      for action in actions:
        conditions_met = True
        if hasattr(action, 'conditions'):
          for condition in action.conditions:
            if 'obj' in condition:
              condition_object = self.objects[condition['obj']]
              checker = getattr(condition_object, condition['check'])
              if 'param' in condition:
                param = condition['param']
                if not checker(param):
                  conditions_met = False
                  break
              else:
                if not checker():
                  conditions_met = False
                  break
            else:
              condition_place = condition['place']
              if State.currentplace.name != condition_place:
                conditions_met = False

        if(conditions_met):
          print(action.text)
          if hasattr(action, 'changes'):
            for change in action.changes:
              if 'obj' in change:
                change_object = self.objects[change['obj']]
                apply_change = getattr(change_object, change['change'])
                param = None
                if 'param' in change:
                  param = change['param']
                if param:
                  apply_change(param)
                else:
                  apply_change()
              else:
                change_place = self.places[change['place']]
                self.changePlace(change_place)

          return True
    return False

  def save(self, name):
    stream = open(name+'.sav', 'w')
    data = dict()
    data['objects'] = self.objects
    data['inventory'] = State.inventory
    data['currentplace'] = State.currentplace
    yaml.dump(data, stream)


  @staticmethod
  def animatedprint(string):
    for c in string:
      sys.stdout.write(c)
      sys.stdout.flush()
      time.sleep(0.001)


class State(object):
  """docstring for State"""
  objects = dict()
  inventory = list()
  currentplace = None





    