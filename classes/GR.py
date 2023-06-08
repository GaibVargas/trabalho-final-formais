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
    self._follow = None

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

  def headFirst(self, head:str, partialFirst: Dict[str, Set[str]], visited: List[str] = []):
    body = self.productions[head]
    visited.append(head)
    for production in body:
      i = 0
      symbol = production[i]
      if symbol in self.terminals or symbol == '&':
        partialFirst[head].add(symbol)
        continue
      if symbol not in visited:
        self.headFirst(symbol, partialFirst, visited)
      symbolFormattedFirst = partialFirst[symbol].copy().difference(set(['&']))
      partialFirst[head] = partialFirst[head].union(symbolFormattedFirst)
      while ('&' in partialFirst[symbol]):
        i += 1
        if i >= len(production):
          partialFirst[head].add('&')
          break
        symbol = production[i]
        if symbol in self.terminals:
          partialFirst[head].add(symbol)
          break
        if symbol not in visited:
          self.headFirst(symbol, partialFirst, visited)
        symbolFormattedFirst = partialFirst[symbol].copy().difference(set(['&']))
        partialFirst[head] = partialFirst[head].union(symbolFormattedFirst)

  def follow(self):
    follow: Dict[str, Set[str]] = {}
    for head in self.productions:
      follow[head] = set()
    follow[self.initial].add('$')
    self.immediateFollow(follow)
    self.indirectFollow(follow)
    self.headToBodyFollow(follow)
    self._follow = follow
    return follow

  def immediateFollow(self, partialFollow: Dict[str, Set[str]]):
    for productions in self.productions.values():
      for production in productions:
        for i, symbol in enumerate(production):
          if i + 1 >= len(production):
            continue
          nextSymbol = production[i + 1]
          if symbol in self.nTerminals and nextSymbol in self.terminals:
            partialFollow[symbol].add(nextSymbol)
    return partialFollow

  def indirectFollow(self, partialFollow: Dict[str, Set[str]]):
    for productions in self.productions.values():
      for production in productions:
        idx = 0
        nextIdx = idx + 1
        while nextIdx < len(production):
          symbol = production[idx]
          while True:
            nextSymbol = production[nextIdx]
            if symbol in self.terminals or nextSymbol in self.terminals:
              break
            if symbol in self.nTerminals and nextSymbol in self.nTerminals:
              first = self._first[nextSymbol].copy().difference(set(['&']))
              partialFollow[symbol] = partialFollow[symbol].union(first)
            if '&' in self._first[nextSymbol] and nextIdx + 1 < len(production):
              nextIdx += 1
            else:
              break
          idx += 1
          nextIdx = idx + 1

    return partialFollow

  def trackHeadToBodyFollowDependencies(self):
    # Informação de dependencia, estrutura do tipo { 'S': ['A', 'B'] }
    dependencies: Dict[str, Set[str]] = {}
    for head in self.productions:
      dependencies[head] = set()

    for head, body in self.productions.items():
      for production in body:
        idx = len(production) - 1
        while True:
          symbol = production[idx]
          if symbol not in self.nTerminals:
            break
          if head != symbol:
            dependencies[head].add(symbol)
          if '&' in self._first[symbol] and idx > 0:
            idx -= 1
          else:
            break
    return dependencies

  def headToBodyFollow(self, partialFollow: Dict[str, Set[str]]):
    dependencies = self.trackHeadToBodyFollowDependencies()
    for head, dependents in dependencies.items():
      for dependent in dependents:
        self.applyHeadToBodyFollow(dependent, head, partialFollow, dependencies)
  
  def applyHeadToBodyFollow(
    self,
    target: str,
    origin: str,
    partialFollow: Dict[str, Set[str]],
    dependencies: Dict[str, Set[str]],
    visited: List[str] = [],
  ):
    visited.append(target)
    partialFollow[target] = partialFollow[target].union(partialFollow[origin])
    dependents = dependencies[target]
    for dependent in dependents:
      if dependent not in visited:
        self.applyHeadToBodyFollow(dependent, target, partialFollow, dependencies, visited)

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