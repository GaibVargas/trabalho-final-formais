import sys
import importlib
from typing import Dict, List, Set
from classes.State import State
from utils.utils import getIdByState, getIdsByStates, getOriginStatesFrom, getTargetStates, getStateById, getDeterministicTargetId, UnionOfLists

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

  def determinize(self):
    if (self.hasEpsilonTransition()):
      self.determinizeWithEpsilon()
      return
    self.determinizeWithoutEpsilon()
  
  def determinizeWithEpsilon(self):
    # Calcular Epsilon Fecho
    epsilonClosure = self.calculateEpsilonClosure()
    # Definir novo estado inicial
    self.excludeEpsilonFromExistingStates(epsilonClosure)
    newInitialStateList = list(epsilonClosure[self.initialState.id])
    newInitialId = getDeterministicTargetId(newInitialStateList)
    if(not self.existsStateWithId(newInitialId)):
      # Não existe estado com 'newInitialId'
      newInitialState = self.createNewStateWithEpsilon(newInitialStateList, epsilonClosure)
      self.initialState = newInitialState
    else: 
      # Já existe o estado com newInitialId
      newInitialState = getStateById(self.states, newInitialId)
      self.initialState = newInitialState
    visited: List[State] = [self.initialState]
    stack: List[State] = [self.initialState]
    while(len(stack) > 0):
      current = stack.pop(0)
      for symbol in self.alphabet:
        targetList = current.getTransitionBySymbol(symbol)
        if(targetList == None):
          continue
        targetId = getDeterministicTargetId(targetList)
        targetState: State = None
        if(self.existsStateWithId(targetId)):
          # Já existe o estado com 'targetId'
          targetState = getStateById(self.states, targetId)
        else:
          # Não existe o estado com 'targetId'
          targetState = self.createNewStateWithEpsilon(targetList, epsilonClosure)
        if(targetState not in visited):
          stack.append(targetState)
          visited.append(targetState)
    self.transformTransitionsIntoDeterministic()
    self.removeUnreachableState()
    for state in self.finalStates:
      if state not in self.states:
        self.finalStates.remove(state)
    print(self)

  def excludeEpsilonFromExistingStates(self, epsilonClosure: dict[str, Set[State]]):
    for state in self.states:
      for symbol in self.alphabet:
        targetList = state.getTransitionBySymbol(symbol)
        if(targetList == None):
          continue
        for target in targetList:
          targetList = UnionOfLists(targetList, list(epsilonClosure[target.id]))
        for targetState in targetList:
          state.addNonExistingTransition(symbol, targetState)
      if(state.transitions.get("&") != None):
        del state.transitions["&"]

  def createNewStateWithEpsilon(self, targetList: List[State], epsilonClosure: dict[str, Set[State]]) -> State:
    newId = getDeterministicTargetId(targetList)
    newState = State(newId)
    for symbol in self.alphabet:
      newStateTargetsWithSymbol: List[State] = []
      for state in targetList:  
        newStateTargetsWithSymbol = UnionOfLists(state.getTransitionBySymbol(symbol), newStateTargetsWithSymbol)
        for targetState in newStateTargetsWithSymbol:
          newStateTargetsWithSymbol = UnionOfLists(newStateTargetsWithSymbol, epsilonClosure[targetState.id])
      for state in newStateTargetsWithSymbol:
        newState.addTransition(symbol, state) 
    # Com estado criado (com as devidas transições),
    # vejamos se ele é estado final ou não e adicionamos à lista de estados
    self.states.append(newState)
    if (len([i for i in targetList if i in self.finalStates]) > 0):
      self.finalStates.append(newState)
    return newState

  def calculateEpsilonClosure(self):
    epsilonClosure: Dict[str, Set[State]] = {}
    for state in self.states:
      visited: List[State] = [state]
      stack: List[State] = [state]
      while(len(stack) > 0):
        current = stack.pop(0)
        stateEpsilonTargetList = current.getTransitionBySymbol('&')
        if(state.id in epsilonClosure):
          epsilonClosure[state.id].add(current)
        else:
          epsilonClosure[state.id] = {current}
        if(stateEpsilonTargetList == None):
          continue
        for target in stateEpsilonTargetList:
          if(target not in visited):
            stack.append(target)
            visited.append(target)
    return epsilonClosure
  
  def determinizeWithoutEpsilon(self):

    visited: List[State] = [self.initialState]
    stack: List[State] = [self.initialState]
    while len(stack) > 0:
      current = stack.pop(0)
      for symbol in self.alphabet:
        currentTargetsList = current.getTransitionBySymbol(symbol)
        if(currentTargetsList == None):
          continue
        currentTargetId = getDeterministicTargetId(currentTargetsList)
        if(self.existsStateWithId(currentTargetId)):
          # Já existe estado com 'currentTargetId'
          targetState = getStateById(self.states, currentTargetId)
          if (targetState not in visited):
            stack.append(targetState)
            visited.append(targetState)
        else:
          # Não existe estado com 'currentTargetId'
          targetState = self.createNewState(currentTargetsList)
          stack.append(targetState)
          visited.append(targetState)
    self.transformTransitionsIntoDeterministic()
    self.removeUnreachableState()
    for state in self.finalStates:
      if state not in self.states:
        self.finalStates.remove(state)
    print(self)
    
          
    
  def createNewState(self, targetList: List[State]) -> State:
    newId = getDeterministicTargetId(targetList)
    newState = State(newId)
    for symbol in self.alphabet:
      newStateTargetsWithSymbol: List[State] = []
      for state in targetList:
        newStateTargetsWithSymbol = UnionOfLists(state.getTransitionBySymbol(symbol), newStateTargetsWithSymbol)
      for state in newStateTargetsWithSymbol:
        newState.addTransition(symbol, state)
    
    # Com estado criado (com as devidas transições),
    # vejamos se ele é estado final ou não e adicionamos à lista de estados

    self.states.append(newState)
    if (len([i for i in targetList if i in self.finalStates]) > 0):
      self.finalStates.append(newState)

    return newState

  def transformTransitionsIntoDeterministic(self):
    # Percorre o automato substituindo transições não deterministicas por deterministicas
    # Ex.: A a [A,B,C] vira A a ABC
    for state in self.states:

      for symbol, states in state.transitions.items():
        if(len(states) > 1):
          state.overwriteTransition(symbol, getStateById(self.states, getDeterministicTargetId(states)))

  def existsStateWithId(self, stateId: str) -> bool:
    if(getStateById(self.states, stateId) == None):
      return False
    return True
    

  def hasEpsilonTransition(self) -> bool:
    for state in self.states:
      if (state.getTransitionBySymbol('&') != None):
        return True
    return False

  def minimize(self):
    self.removeUnreachableState()
    self.removeDeadStates()    
    self.removeEquivalentStates()

  def test(self, word: str):
    currentState = self.initialState
    for letter in word:
      if letter not in self.alphabet:
        return False
      nextState = currentState.deterministicTransition(letter)
      if (not nextState):
        return False
      currentState = nextState
    if (currentState not in self.finalStates):
      return False
    return True

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