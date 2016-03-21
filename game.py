import yaml, time, sys
from collections import deque

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
    State.actionsleft = gamedata['startactions']
    State.money = gamedata['startmoney']
    State.drawpile = deque(gamedata['startdrawpile'])
    State.sandrapile = deque(gamedata['startsandrapile'])
    State.sandrahand = gamedata['startsandrahand']

    State.startactions = gamedata['startactions']
    State.startmoney = gamedata['startmoney']
    State.startdrawpile = gamedata['startdrawpile']
    State.startsandrapile = gamedata['startsandrapile']
    State.startsandrahand = gamedata['startsandrahand']
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
    State.actionsleft = gamedata['actionsleft']
    State.money = gamedata['money']
    State.drawpile = deque(gamedata['drawpile'])
    State.sandrahand = gamedata['sandrahand']
    State.sandrapile = deque(gamedata['sandrapile'])
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
            if not take_obj.isDestroyed():
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
          Game.animatedprint(action.text)
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
                if 'place' in change:
                  change_place = self.places[change['place']]
                  self.changePlace(change_place)
                else:
                  if 'drawCard' in change:
                    amount = change['drawCard']
                    self.drawCard(amount)
                  else:
                    if 'actionDiff' in change:
                      diff = change['actionDiff']
                      self.adjustActions(diff)
                    else:
                      if 'specialAction' in change:
                        self.specialAction(change['specialAction'])
                      else:
                        print("unknownchange")

          return True
    return False

  def drawCard(self, amount):
    Game.animatedprint("Du ziehst " + str(amount) + " Karten von deinem Nazistapel: \n")
    for _ in range(amount):
      card = self.objects[State.drawpile.popleft()][0]
      card.activate()
      card.toInventory()
      Game.animatedprint(card.name + "\n")


  def adjustActions(self, diff):
    if (diff == 1):
      Game.animatedprint("+ " + str(diff) + " Aktion. \n")
    else: 
      if (diff > 1):
          Game.animatedprint("+ " + str(diff) + " Aktionen. \n")
    State.actionsleft += (diff - 1)
    Game.animatedprint("Übrige Aktionen: " + str(State.actionsleft) + "\n")

  def specialAction(self, cardname):
    switcher = {
      'maskerade': self.maskerade,
      'miliz': self.miliz,
      'raeuber': self.raeuber,
      'dieb': self.dieb
    }

    func = switcher.get(cardname)
    func()
    self.checkDominion()

  def save(self, name):
    stream = open(name+'.sav', 'w')
    data = dict()
    data['objects'] = self.objects
    data['inventory'] = State.inventory
    data['currentplace'] = State.currentplace
    data['actionsleft'] = State.actionsleft
    data['money'] = State.money
    data['drawpile'] = State.drawpile
    data['sandrapile'] = State.sandrapile
    data['sandrahand'] = State.sandrahand
    yaml.dump(data, stream)

  def resetDominion(self, message):
    Game.animatedprint(message + '\n')
    self.objects['laboratorium'][0].destroy()
    self.objects['laboratorium'][0].toInventory()
    self.objects['dorf'][0].destroy()
    self.objects['maskerade'][0].destroy()
    self.objects['grenzdorf'][0].destroy()
    self.objects['miliz'][0].destroy()
    self.objects['dieb'][0].destroy()
    self.objects['räuber'][0].destroy()
    self.objects['anwesen'][0].destroy()
    State.drawpile = deque(State.startdrawpile)
    State.sandrahand = list(State.startsandrahand)
    State.actionsleft = State.startactions
    State.money = State.startmoney
    State.sandrapile = deque(State.startsandrapile)

  def checkDominion(self):
    if State.actionsleft == 0 and State.money < 150:
      self.resetDominion("Ich habe keine Aktionen mehr und nicht genug Geld geklaut.. Gut, dass ich mir die gesamte Combo nur im Kopf vorgestellt habe.")
    if State.actionsleft == 0 and State.money == 150:
      self.changePlace(self.places["fahrt.kielpb.ende"])
      self.changePlace(self.places["paderborn.waldrand"])


  @staticmethod
  def animatedprint(string):
    for c in string:
      sys.stdout.write(c)
      sys.stdout.flush()
      time.sleep(0.002)
  @staticmethod
  def addOrAppendToDict(d, key, newvalue):
    if key in d:
      oldvalue = d[key]
      oldvalue.append(newvalue)
      d[key] = oldvalue
    else:
      d[key] = list([newvalue])

### DOMINION ACTIONS!
  def maskerade(self):
    sandracard = self.objects[State.sandrahand.pop()][0]
    mycard = self.objects['anwesen'][0]
    if not mycard.isInInventory():
      self.resetDominion('Ich habe keinen Schrott, den ich Sandra geben könnte.. gut, dass ich mir die gesamte Combo nur im Kopf vorgestellt habe..\n')
    else:
      State.sandrahand.append(mycard.name)
      if sandracard.name == 'fuffi':
        State.money += 50
        Game.animatedprint("Ich gebe Sandra ein Anwesen und bekomme von ihr einen Fuffi. Ich habe jetzt " + str(State.money) + " Euro geklaut. \n")
        mycard.destroy()

  def miliz(self):
    for _ in range(2):
        sandracard = State.sandrahand.pop()
        State.sandrapile.append(sandracard)
    Game.animatedprint("Sandra legt zwei Karten ab. \n")
  def dieb(self):
    stolen = False
    for _ in range(2):
      if (len(State.sandrapile) > 0):
        sandracard = State.sandrapile[0]
        if 'fuffi' == sandracard:
          if not stolen:
            stolen = True
            State.money += 50
            State.sandrapile.remove(sandracard)
            Game.animatedprint('Sandra deckt einen Fuffi von ihrem Ablagestapen auf. Sie zerreißt ihn vor meinen Augen und in meiner Hosentasche erscheint ein Fuffi auf magische Art und Weise. Ich habe jetzt ' + str(State.money) + " Euro geklaut.\n")
          else:
            State.sandrapile.rotate(-1)
            Game.animatedprint('Sandra deckt einen weiteren Fuffi auf und legt ihn ab.\n')
        else:
          State.sandrapile.rotate(-1)
          Game.animatedprint('Sandra deckt die Karte ' + sandracard + ' auf und legt sie ab.\n')

  def raeuber(self):
    stolen = False
    for _ in range(2):
      if (len(State.sandrapile) > 0):
        sandracard = State.sandrapile[0]
        if 'fuffi' == sandracard:
          if not stolen:
            stolen = True
            State.money += 50
            State.sandrapile.remove(sandracard)
            Game.animatedprint('Sandra deckt einen Fuffi von ihrem Ablagestapen auf. Sie zerreißt ihn vor meinen Augen und in meiner Hosentasche erscheint ein Fuffi auf magische Art und Weise. Ich habe jetzt ' + str(State.money) + " Euro geklaut.\n")
          else:
            State.sandrapile.rotate(-1)
            Game.animatedprint('Sandra deckt einen weiteren Fuffi auf und legt ihn ab.\n')
        else:
          State.sandrapile.rotate(-1)
          Game.animatedprint('Sandra deckt die Karte ' + sandracard + ' auf und legt sie ab.\n')
    if not stolen:
      Game.animatedprint('Sandra muss sich ein 5 Cent Stück nehmen, weil ich kein Geld geklaut habe.\n')

class State(object):
  """docstring for State"""
  objects = dict()
  inventory = list()
  currentplace = None

  "Dominion stuff"
  actionsleft = 1
  money = 0
  drawpile = list()
  sandrapile = list()
  sandrahand = list()

  startactions = 1
  startmoney = 0
  startdrawpile = list()
  startsandrapile = list()
  startsandrahand = list()








    