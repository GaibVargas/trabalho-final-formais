import importlib
from typing import Dict, List
from classes.State import State
from utils.utils import getIdByState, getIdsByStates, getOriginStatesFrom, getTargetStates

class AF:
  def __init__(
    self,
    alphabet: List[str],
    states: List[State],
    initialState: State,
    finalStates: List[State],
  ):
    self.alphabet = alphabet
    self.states = states
    self.initialState = initialState
    self.finalStates = finalStates

  def parseToGR(self):
    GRModule = importlib.import_module('classes.GR')
    GR = GRModule.GR
    # TODO: primeiro determinizar o autômato e minimizá-lo
    productions: Dict[str, List[str]] = {}
    for state in self.states:
      for symbol, body in state.transitions.items():
        for target in body:
          if state.id not in productions:
            productions[state.id] = [f'{symbol}{target.id}']
          else:
            productions[state.id].append(f'{symbol}{target.id}')
          if target in self.finalStates:
            productions[state.id].append(symbol)
    
    nTerminals = list(map(lambda x: x.id, self.states))
    initialProducion = self.initialState.id
    if self.initialState in self.finalStates:
      productions['Inicial'] = [*productions[self.initialState.id], '&']
      initialProducion = 'Inicial'
      nTerminals.append('Inicial')

    return GR(
      self.alphabet.copy(),
      nTerminals,
      initialProducion,
      productions
    )

  def unreachableStates(self):
    visited: List[State] = [self.initialState]
    stack: List[State] = [self.initialState]
    while len(stack) > 0:
      current = stack.pop(0)
      targetStates = getTargetStates(current)
      for targetState in targetStates:
        if targetState not in visited:
          visited.append(targetState)
          stack.append(targetState)
    return list(filter(lambda x: x not in visited, self.states))

  def removeDeadStatesTransitions(self, deadStates: List[State]):
    for state in self.states:
      deleteTransitions: List[str] = []
      for key, values in state.transitions.items():
        transitions = list(filter(lambda x: x not in deadStates, values))
        if len(transitions) > 0:
          state.transitions[key] = transitions
        else:
          deleteTransitions.append(key)
      for transitionSymbol in deleteTransitions:
        del state.transitions[transitionSymbol]

  def deadStates(self):
    visited: List[State] = self.finalStates.copy()
    stack: List[State] = self.finalStates.copy()
    while len(stack) > 0:
      current = stack.pop(0)
      originStates = getOriginStatesFrom(self.states, current)
      for state in originStates:
        if state not in visited:
          visited.append(state)
          stack.append(state)
    deadStates = list(filter(lambda x: x not in visited, self.states))
    self.removeDeadStatesTransitions(deadStates)
    return deadStates

  def minimize(self):
    unreachableStates = self.unreachableStates()
    reachableStates = list(filter(lambda x: x not in unreachableStates, self.states))
    self.states = reachableStates

    deadStates = self.deadStates()
    nonDeadStates = list(filter(lambda x: x not in deadStates, self.states))
    self.states = nonDeadStates

    print(self)

  def __str__(self):
    transicoes = ""
    for state in self.states:
      transicoes += state.stringify()
    return (
      "\nAUTÔMATO FINITO\n"
      f"Estados: {getIdsByStates(self.states)}\n"
      f"Estado Inicial: {getIdByState(self.initialState)}\n"
      f"Estados Finais: {getIdsByStates(self.finalStates)}\n"
      f"Transições:\n"
      f"{transicoes}"
    )