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
  
  def getTransitionBySymbol(self, symbol: str):
    if symbol in self.transitions:
      return self.transitions[symbol]
    return None

  def stringifyTransitions(self):
    response = ""
    for symbol, transitions in self.transitions.items():
      response += f'\t({self.id}, {symbol}): {list(map(lambda x: x.id, transitions))}\n'
    return response
  
  def stringify(self):
    return self.stringifyTransitions()

  def __lt__(self, other: 'State'):
    return self.id < other.id