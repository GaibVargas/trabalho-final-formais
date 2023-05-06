from typing import List
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

  def __str__(self):
    transicoes = ""
    for state in self.states:
      transicoes += state.stringify()
    return (
      f"Estados: {getIdsByStates(self.states)}\n"
      f"Estado Inicial: {getIdByState(self.initialState)}\n"
      f"Estados Finais: {getIdsByStates(self.finalStates)}\n"
      f"Transições:\n"
      f"{transicoes}"
    )