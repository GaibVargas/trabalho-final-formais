import importlib
from typing import Dict, List
from classes.State import State
from utils.utils import getIdByState, getIdsByStates

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