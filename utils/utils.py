import sys
import time
from typing import List, Set, TypeVar
from classes.State import State

T = TypeVar('T')

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

def UnionOfLists(list1: List[T], list2: List[T]) -> List[T]:
    try:
      final_list = list(set(list1) | set(list2))
    except:
      if(type(list1) == List):
        return list1
      return list2
    return final_list

def getRepeatedElementsOfAList(lista: List[T]) -> List[T]:
  visited: List[T] = []
  repeated: Set[T] = set()
  for element in lista:
    if(element in visited):
      repeated.add(element)
    visited.append(element)
  return list(repeated)

def archivePrint(filename: str, content):
  dir = 'results'
  prefix = int(time.time())
  filename = f'{dir}/{prefix}-{filename}.txt'
  with open(filename, 'w') as arquivo:
    sys.stdout = arquivo
    print(content)
    sys.stdout = sys.__stdout__
