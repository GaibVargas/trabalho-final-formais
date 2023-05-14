from typing import List, Set
from classes.State import State

def getStateById(states: List[State], id: str):
  for state in states:
    if state.id == id:
      return state

def getIdByState(state: State):
  return state.id

def getIdsByStates(states: List[State]):
  return list(map(lambda x: getIdByState(x), states))

def getTargetStates(origin: State):
  targetStates: Set[State] = set()
  for transition in origin.transitions.values():
    targetStates.update(transition)
  return list(targetStates)

def getOriginStatesFrom(states: List[State], target: State):
  originStates: Set[State] = set()
  for state in states:
    for transition in state.transitions.values():
      if target in transition:
        originStates.add(state)
  return list(originStates)