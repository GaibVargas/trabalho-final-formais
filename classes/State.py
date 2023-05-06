from typing import Dict, List

class State:
  def __init__(self, id: str, isFinal: bool):
    self.id = id
    self.isFinal = isFinal
    self.transitions: Dict[str, List[State]] = {}
  
  def addTransition(self, symbol: str, target: 'State'):
    if symbol not in self.transitions:
      self.transitions[symbol] = [target]
    else:
      self.transitions[symbol].append(target)
  
  def stringifyTransitions(self):
    response = ""
    for symbol, transitions in self.transitions.items():
      response += f'\t({self.id}, {symbol}): {list(map(lambda x: x.id, transitions))}\n'
    return response
  
  def stringify(self):
    return self.stringifyTransitions()