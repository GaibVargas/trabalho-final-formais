import importlib
from typing import Dict, List, Set
from classes.State import State
from utils.utils import getStateById

class GR:
  def __init__(
    self,
    terminals: List[str],
    nTerminals: List[str],
    initial: str,
    productions: Dict[str, List[str]]
  ):
    self.terminals = terminals
    self.nTerminals = nTerminals
    self.initial = initial
    self.productions = productions
    self._first = None

  def parseToAF(self):
    AFModule = importlib.import_module('classes.AF')
    AF = AFModule.AF
    states: List[State] = []
    for nTerminal in self.nTerminals:
      states.append(State(nTerminal))

    finalStates: List[State] = []
    finalState = State('Final')
    finalStates.append(finalState)
    states.append(finalState)

    initialState = getStateById(states, self.initial)

    for head, body in self.productions.items():
      state = getStateById(states, head)
      for transition in body:
        if len(transition) > 1:
          symbol, *next = transition
          target = getStateById(states, ''.join(next))
          state.addTransition(symbol, target)
        else:
          target = getStateById(states, 'Final')
          if head == self.initial and transition == '&':
            finalStates.append(initialState)
          else:
            state.addTransition(transition, target)
    
    return AF(
      self.terminals.copy(),
      states,
      initialState,
      finalStates,
    )

  def first(self):
    first: Dict[str, Set[str]] = {}
    for head in self.productions:
      first[head] = set()
    for head in self.productions:
      if len(first[head]) == 0:
        self.headFirst(head, first)
    self._first = first
    return first

  def headFirst(self, head:str, parcialFirst: Dict[str, Set[str]]):
    body = self.productions[head]
    for production in body:
      i = 0
      symbol = production[i]
      if symbol in self.terminals or symbol == '&':
        parcialFirst[head].add(symbol)
        continue
      
      self.headFirst(symbol, parcialFirst)
      symbolFormattedFirst = parcialFirst[symbol].copy().difference(set(['&']))
      parcialFirst[head] = parcialFirst[head].union(symbolFormattedFirst)
      while ('&' in parcialFirst[symbol]):
        i += 1
        if i >= len(production):
          parcialFirst[head].add('&')
          break
        symbol = production[i]
        if symbol in self.terminals:
          parcialFirst[head].add(symbol)
          break
        self.headFirst(symbol, parcialFirst)
        symbolFormattedFirst = parcialFirst[symbol].copy().difference(set(['&']))
        parcialFirst[head] = parcialFirst[head].union(symbolFormattedFirst)

  def naiveFirst(self):
    result: Dict[str, Set[str]] = {}
    for head, body in self.productions.items():
      for production in body:
        first = production[0]
        if head in result:
          result[head].add(first)
        else:
          result[head] = set([first])
    return result

  def __str__(self):
    productions = ''
    for head, body in self.productions.items():
      productions += f"\t{head} -> {body}\n"
    return (
      "\nGRAMÁTICA\n"
      f"Terminais: {self.terminals}\n"
      f"Não terminais: {self.nTerminals}\n"
      f"Produção inicial: {self.initial}\n"
      "Produções:\n"
      f"{productions}"
    )