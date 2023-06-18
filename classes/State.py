from typing import Dict, List

class State:
  def __init__(self, id: str):
    self.id = id
    self.transitions: Dict[str, List[State]] = {}

  def deterministicTransition(self, symbol: str):
    if symbol not in self.transitions.keys():
      return None
    return self.transitions[symbol][0]

  def addTransition(self, symbol: str, target: 'State'):
    if symbol not in self.transitions:
      self.transitions[symbol] = [target]
    else:
      self.transitions[symbol].append(target)
  
  def addNonExistingTransition(self, symbol: str, target: 'State'):
    if symbol not in self.transitions:
      self.transitions[symbol] = [target]
    elif(target not in self.transitions[symbol]):
        self.transitions[symbol].append(target)

  def getTransitionBySymbol(self, symbol: str):
    if symbol in self.transitions:
      return self.transitions[symbol]
    return None

  def stringifyTransitions(self):
    response = ""
    for symbol, transitions in self.transitions.items():
      for transition in transitions:
        response += f'\n{self.id} {symbol} {transition.id}'
    return response
  
  def overwriteTransition(self, symbol: str, newTarget: 'State'):
      self.transitions[symbol] = [newTarget]


  def stringify(self):
    return self.stringifyTransitions()

  def __lt__(self, other: 'State'):
    return self.id < other.id
  