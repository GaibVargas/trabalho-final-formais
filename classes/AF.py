import sys
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

  def removeUnreachableState(self):
    visited: List[State] = [self.initialState]
    stack: List[State] = [self.initialState]
    while len(stack) > 0:
      current = stack.pop(0)
      targetStates = getTargetStates(current)
      for targetState in targetStates:
        if targetState not in visited:
          visited.append(targetState)
          stack.append(targetState)
    unreachableStates = list(filter(lambda x: x not in visited, self.states))
    reachableStates = list(filter(lambda x: x not in unreachableStates, self.states))
    self.states = reachableStates

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

  def updateStatesTransitions(self, changeFrom: List[State], changeTo: State):
    for state in self.states:
      for key, values in state.transitions.items():
        newTransitions: List[State] = []
        for target in values:
          if target in changeFrom:
            newTransitions.append(changeTo)
          else:
            newTransitions.append(target)
        state.transitions[key] = newTransitions

  def removeDeadStates(self):
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
    nonDeadStates = list(filter(lambda x: x not in deadStates, self.states))
    self.states = nonDeadStates

  def removeEquivalentStates(self):
    # grupos de equivalência baseados em chave de transição
    groups = {
      '0': self.finalStates.copy(),
      '1': list(filter(lambda x: x not in self.finalStates, self.states))
    }
    currentGroups: Dict[str, List[State]] = {}
    while True:
      for equivalentKey, states in groups.items():
        # cria a próxima chave do estado baseado nas suas transições
        for state in states:
          transitionToGroup: List[str] = [equivalentKey]
          for symbol in self.alphabet:
            transitions = state.getTransitionBySymbol(symbol)
            if transitions == None:
              transitionToGroup.append('None')
              continue
            if len(transitions) > 1:
              print('Erro: Transição não determinística')
              sys.exit(1)
            targetState = transitions[0]
            # verifica em qual grupo de equivalência está o alvo da transição
            for targetEquivalentKey, targetStates in groups.items():
              if targetState in targetStates:
                transitionToGroup.append(targetEquivalentKey)
                break
          # cria chave dos novos grupos
          transitionToGroupKey = '-'.join(transitionToGroup)
          if transitionToGroupKey in currentGroups:
            currentGroups[transitionToGroupKey].append(state)
          else:
            currentGroups[transitionToGroupKey] = [state]
      if sorted(groups.values()) == sorted(currentGroups.values()):
        break
      else:
        groups = currentGroups.copy()
        currentGroups = {}
    
    # remove estados equivalentes do autômato e substituí as transições
    equivalentStates: Dict[State, List[State]] = {}
    for states in groups.values():
      if len(states) == 1:
        continue
      baseState, *restStates = states
      equivalentStates[baseState] = restStates
    removedStates: List[State] = []
    for baseState, restStates in equivalentStates.items():
      self.updateStatesTransitions(restStates, baseState)
      removedStates.extend(restStates)
      for v in restStates:
        if v == self.initialState:
          self.initialState = baseState
        if v in self.finalStates:
          self.finalStates.remove(v)
          if baseState not in self.finalStates:
            self.finalStates.append(baseState)
    self.states = list(filter(lambda x: x not in removedStates, self.states))

  def minimize(self):
    self.removeUnreachableState()
    self.removeDeadStates()    
    self.removeEquivalentStates()

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