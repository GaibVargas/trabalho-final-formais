from typing import List
from classes.State import State

def getStateById(states: List[State], id: str):
  for state in states:
    if state.id == id:
      return state

def getIdByState(state: State):
  return state.id

def getIdsByStates(states: List[State]):
  return list(map(lambda x: getIdByState(x), states))