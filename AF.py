import sys
from typing import List
from State import State

class AF:
  def __init__(
    self,
    alphabet: List[str],
    stateIds: List[str],
    initial: str,
    finals: List[str],
    transitions: List[str],
  ):
    self.states: List[State] = []
    self.alphabet = alphabet
    self.stateIds = stateIds
    self.initialStateId = initial
    self.finalStateIds = finals
    self.setupStates(transitions)
  
  def setupStates(self, transitions):
    for id in self.stateIds:
      state = State(id, id in self.finalStateIds)
      self.states.append(state)
    for transition in transitions:
      fromId, symbol, targetId = transition.split(' ')
      self.addTransition(fromId, symbol, targetId)

  def addTransition(self, fromId: str, symbol:str, targetId:str):
    if symbol not in self.alphabet and symbol != '&':
      print(f'Erro ao adicionar transições, {symbol} não faz parte do alfabeto')
    fromState = self.getStateById(fromId)
    targetState = self.getStateById(targetId)
    if not fromState:
      print(f'Erro ao adicionar transições ao estado {fromId}')
      sys.exit(1)
    if not targetState:
      print(f'Erro ao adicionar transições ao estado {fromId}, alvo {targetId} não encontrado')
    fromState.addTransition(symbol, targetState)

  def getStateById(self, id):
    for state in self.states:
      if state.id == id:
        return state

  def __str__(self):
    transicoes = ""
    for state in self.states:
      transicoes += state.stringify()
    return (
      f"Estados: {self.stateIds}\n"
      f"Estado Inicial: {self.initialStateId}\n"
      f"Estados Finais: {self.finalStateIds}\n"
      f"Transições:\n"
      f"{transicoes}"
    )