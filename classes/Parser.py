import sys
from typing import List
from classes.AF import AF
from classes.State import State
from utils.utils import getStateById

class Parser:
  def addTransition(self, states: List[State], fromId: str, symbol: str, targetId: str):
    fromState = getStateById(states, fromId)
    targetState = getStateById(states, targetId)
    if not fromState or not targetState:
      print(f'Erro ao adicionar transição ({fromId}, {symbol}): {targetId}')
      sys.exit(1)
    fromState.addTransition(symbol, targetState)

  def textToAF(
    self,
    alphabet: str,
    states: str,
    initial: str,
    finals: str,
    transitions: str
  ) -> AF:
    # Sanitiza entradas retirando espaços em branco e enter, e formata entrada
    sanitized_alphabet = alphabet.strip().split(',')
    sanitized_states = states.strip().split(',')
    sanitized_initial = initial.strip()
    sanitized_finals = finals.strip().split(',')
    sanitized_transitions = list(map(lambda x: x.strip().split(' '), transitions))
    # Cria estados do autômato
    created_states: List[State] = []
    for id in sanitized_states:
      state = State(id, id in sanitized_finals)
      created_states.append(state)
    # Cria transições do autômato
    for transition in sanitized_transitions:
      fromId, symbol, targetId = transition
      if symbol not in sanitized_alphabet and symbol != '&':
        print(f'Erro ao adicionar transições, {symbol} não faz parte do alfabeto')
        sys.exit(1)
      self.addTransition(created_states, fromId, symbol, targetId)
    
    initialState = getStateById(created_states, sanitized_initial)

    return AF(
      sanitized_alphabet,
      created_states,
      initialState,
      list(map(lambda x: getStateById(created_states, x) ,sanitized_finals)),
    )
