import cmd, sys
from game import Game
from item import Item
from place import Place
from action import Action

class Controller(cmd.Cmd):
  """docstring for Controller"""
  file = None

  #Basic commands
  def do_untersuche(self, arg):
    'Untersuche einen Gegenstand: UNTERSUCHE Bett'
    self.game.examine(arg)

  def do_umsehen(self, arg):
    'Sehe dich am aktuellen Ort um.'
    self.game.umsehen()

  def do_speichern(self, arg):
    self.game.save(arg)

  def do_nehme(self, arg):
    'Nehme einen Gegenstand auf'
    self.game.take(arg)

  def do_benutze(self, arg):
    'Benutze ein Objekt oder zwei Objekte miteinander: BENUTZE Schalter / BENUTZE Becher Wasserhahn'
    self.game.use(arg)

  def do_gehe(self, arg):
    'Gehe in eine Richtung oder zu einem Objekt'
    self.game.go(arg)

  def do_newgame(self, arg):
    self.game = Game()

  def do_lade(self, arg):
    self.game = Game(arg)

  def do_inventar(self, arg):
    self.game.checkInventory()
    
  def do_mache_bratkartoffeln(self, arg):
    'Bereite wenn moeglich Bratkartoffeln zu! : MACHE BRATKARTOFFELN'
    print("Ich habe gerade keinen Hunger.")

  def precmd(self, line):
    if not hasattr(self, 'game'):
      if line != "newgame" and line != "?" and not line.startswith("lade"):
        print("Du solltest zuerst ein Spiel starten / laden.")
        return ""
    return line.lower()

  def default(self, arg):
    if hasattr(self, 'game'):
      print("Ich weiss nicht was ich tuen soll...")

if __name__ == '__main__':
  Controller().cmdloop()