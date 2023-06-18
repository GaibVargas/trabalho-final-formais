from typing import List, Set
from classes.State import State

def getStateById(states: List[State], id: str):
  for state in states:
    if state.id == id:
      return state
  return None

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

def getDeterministicTargetId(targetList: List[State]) -> State:
    # Dada uma lista de estados, junta os ID's dos estados e retorna o ID resultante

    targetIdList: List[str] = []
    for targetState in targetList:
      targetIdList.append(targetState.id)
    targetIdList.sort()
    targetId = "".join(targetIdList)
    return targetId

def UnionOfLists(list1: List[any], list2: List[any]):
    try:
      final_list = list(set(list1) | set(list2))
    except:
      if(type(list1) == List):
        return list1
      return list2
    return final_list