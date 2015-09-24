import yaml, time, sys

class Game(object):
  """
      This is the main class. A Game instance holds all data needed to play the game.
      Therefore the Game-YAML is parsed and all the Items / Places / Actions get initialized.

      This class also executes the operations.

      To write a own game a own yaml-file has to be configured.
  """

  def __init__(self, loadfile = None):
    super(Game, self).__init__()
    stream = open("batzgame.yaml", 'r')
    gamedata = yaml.load(stream)
    self.objects = dict()
    #allow multiple names
    for o in gamedata['objects']:
      Game.addOrAppendToDict(self.objects, o.name, o)

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
    #Itemsveränderungen übernehmen
    for o_name in gamedata['objects']:
      for o in gamedata['objects'][o_name]:
        for current_obj in self.objects[o_name]:
          if current_obj.getID() == o.getID():
            current_obj.copyFrom(o)

    State.inventory = gamedata['inventory']
    self.changePlace(self.places[gamedata['currentplace'].name])

  def initNewGame(self):
    Game.animatedprint(self.introduction)
    #time.sleep(3)
    self.changePlace(self.startplace)

  def addAction(self, action):
    if hasattr(action, 'target2'):
      Game.addOrAppendToDict(self.actions, action.operation + action.target + ' ' + action.target2, action)
      Game.addOrAppendToDict(self.actions, action.operation + action.target2 + ' ' + action.target, action)
    else:
      if hasattr(action, 'target'):
        Game.addOrAppendToDict(self.actions, action.operation + action.target, action)
      else:
        Game.addOrAppendToDict(self.actions, action.operation, action)

  def changePlace(self, where):
    State.currentplace = where
    Game.animatedprint(where.description)

  def examine(self, what):
    if what in self.objects:
      items = self.objects[what]
      for item in items:
        if item.isActive() and (item.isInInventory() or item.isAt(State.currentplace.name)):
          Game.animatedprint(item.description)
          return
    Game.animatedprint("Ich kann "+what+" nicht finden.\n")

  def use(self, what):
    if not self.executeOperation(what, "benutze"):
      print("Nichts besonderes passiert.")

  def take(self, what):
    if what in self.objects:
      for take_obj in self.objects[what]:
        if take_obj.isActive() and take_obj.isNotInInventory() and take_obj.isAt(State.currentplace.name):
          if self.executeOperation(what, "nehme"):
            take_obj.toInventory()
            return
    print("Das kann ich nicht tun.")

  def go(self, where):
    if not self.executeOperation(where, "gehe"):
      print("Das kann ich nicht tun")
  def thumbup(self):
      if not self.executeOperation(None, "daumenraus"):
        print("Ich halte den Daumen raus... nichts geschieht.")
  def checkInventory(self):
    for item in State.inventory:
      print(item)

  def umsehen(self):
    print(State.currentplace.description)

  def executeOperation(self, what, operation):
    if what:
      actioncode = operation+what
    else:
      actioncode = operation
    if actioncode in self.actions:
      actions = self.actions[actioncode]
      for action in actions:
        conditions_met = True
        if hasattr(action, 'conditions'):
          for condition in action.conditions:
            if 'obj' in condition:
              obj_name = condition['obj']
              if 'id' in condition:
                obj_id = condition['id']
              else:
                obj_id = 0  
              for condition_object in self.objects[obj_name]:
                if condition_object.getID() == obj_id:
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
                obj_name = change['obj']
                if 'id' in change:
                  obj_id = change['id']
                else:
                  obj_id = 0
                for change_object in self.objects[obj_name]:
                  if change_object.getID() == obj_id:
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
  @staticmethod
  def addOrAppendToDict(d, key, newvalue):
    if key in d:
      oldvalue = d[key]
      oldvalue.append(newvalue)
      d[key] = oldvalue
    else:
      d[key] = list([newvalue])


class State(object):
  """docstring for State"""
  objects = dict()
  inventory = list()
  currentplace = None





    