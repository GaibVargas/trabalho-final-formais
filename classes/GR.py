import importlib
from typing import Dict, List, Set, Tuple
from classes.State import State
from utils.utils import getStateById, getRepeatedElementsOfAList

class GR:
  def __init__(
    self,
    terminals: List[str],
    nTerminals: List[str],
    initial: str,
    productions: Dict[str, List[str]]
  ):
    self.terminals = terminals
    self.nTerminals = nTerminals
    self.initial = initial
    self.productions = productions
    self._first = None
    self._follow = None

  def parseToAF(self):
    AFModule = importlib.import_module('classes.AF')
    AF = AFModule.AF
    states: List[State] = []
    for nTerminal in self.nTerminals:
      states.append(State(nTerminal))

    finalStates: List[State] = []
    finalState = State('Final')
    finalStates.append(finalState)
    states.append(finalState)

    initialState = getStateById(states, self.initial)

    for head, body in self.productions.items():
      state = getStateById(states, head)
      for transition in body:
        if len(transition) > 1:
          symbol, *next = transition
          target = getStateById(states, ''.join(next))
          state.addTransition(symbol, target)
        else:
          target = getStateById(states, 'Final')
          if head == self.initial and transition == '&':
            finalStates.append(initialState)
          else:
            state.addTransition(transition, target)
    
    return AF(
      self.terminals.copy(),
      states,
      initialState,
      finalStates,
    )

  def first(self):
    first: Dict[str, Set[str]] = {}
    for head in self.productions:
      first[head] = set()
    for head in self.productions:
      self.headFirst(head, first)
    self._first = first
    return first

  # Calcula o first da cabeça de produção de forma recursiva
  def headFirst(self, head:str, partialFirst: Dict[str, Set[str]], visited: List[str] = []):
    body = self.productions[head]
    visited.append(head)
    for production in body:
      i = 0
      symbol = production[i]
      # Se o primeiro símbolo for não terminal, coloca no conjunto e passa para próxima produção
      if symbol in self.terminals or symbol == '&':
        partialFirst[head].add(symbol)
        continue
      # Se for um não terminal descubra seu first
      if symbol not in visited:
        self.headFirst(symbol, partialFirst, visited)
      # Retira o & e faz união com o conjunto atual
      symbolFormattedFirst = partialFirst[symbol].copy().difference(set(['&']))
      partialFirst[head] = partialFirst[head].union(symbolFormattedFirst)
      # Se o first do não terminal possuir &, continua pela produção para completar o conjunto first
      while ('&' in partialFirst[symbol]):
        i += 1
        if i >= len(production):
          partialFirst[head].add('&')
          break
        symbol = production[i]
        if symbol in self.terminals:
          partialFirst[head].add(symbol)
          break
        if symbol not in visited:
          self.headFirst(symbol, partialFirst, visited)
        symbolFormattedFirst = partialFirst[symbol].copy().difference(set(['&']))
        partialFirst[head] = partialFirst[head].union(symbolFormattedFirst)

  def follow(self):
    follow: Dict[str, Set[str]] = {}
    for head in self.productions:
      follow[head] = set()
    follow[self.initial].add('$')
    self.immediateFollow(follow)
    self.indirectFollow(follow)
    self.headToBodyFollow(follow)
    self._follow = follow
    return follow

  # Calula follow imediato, ex: produções que contenham algo do tipo Na
  def immediateFollow(self, partialFollow: Dict[str, Set[str]]):
    for productions in self.productions.values():
      for production in productions:
        for i, symbol in enumerate(production):
          # Se for produção unitária passa para próxima produção da cabeça
          if i + 1 >= len(production):
            continue
          nextSymbol = production[i + 1]
          if symbol in self.nTerminals and nextSymbol in self.terminals:
            partialFollow[symbol].add(nextSymbol)
    return partialFollow

  # Calcula follow para produções que contenham do tipo AB
  def indirectFollow(self, partialFollow: Dict[str, Set[str]]):
    for productions in self.productions.values():
      for production in productions:
        idx = 0
        nextIdx = idx + 1
        while nextIdx < len(production):
          symbol = production[idx]
          # Enquanto o símbolo à direita for um não terminal e conter & em seu first faça:
          while True:
            nextSymbol = production[nextIdx]
            if symbol in self.terminals or nextSymbol in self.terminals:
              break
            if symbol in self.nTerminals and nextSymbol in self.nTerminals:
              first = self._first[nextSymbol].copy().difference(set(['&']))
              partialFollow[symbol] = partialFollow[symbol].union(first)
            if '&' in self._first[nextSymbol] and nextIdx + 1 < len(production):
              nextIdx += 1
            else:
              break
          idx += 1
          nextIdx = idx + 1

    return partialFollow

  # Informação de dependencia, estrutura do tipo { 'S': ['A', 'B'] }
  # Faz rastreamento para o passo de colocar o Follow(Head) no Follow(N)
  # sendo N o último não terminal da produção
  def trackHeadToBodyFollowDependencies(self):
    dependencies: Dict[str, Set[str]] = {}
    for head in self.productions:
      dependencies[head] = set()

    for head, body in self.productions.items():
      for production in body:
        # Percorre produção de trás para frente
        idx = len(production) - 1
        # Enquanto último símbolo for não terminal e & pertencer ao seu first, faça:
        while True:
          symbol = production[idx]
          if symbol not in self.nTerminals:
            break
          if head != symbol:
            dependencies[head].add(symbol)
          if '&' in self._first[symbol] and idx > 0:
            idx -= 1
          else:
            break
    return dependencies

  def headToBodyFollow(self, partialFollow: Dict[str, Set[str]]):
    dependencies = self.trackHeadToBodyFollowDependencies()
    for head, dependents in dependencies.items():
      for dependent in dependents:
        self.applyHeadToBodyFollow(dependent, head, partialFollow, dependencies)

  # Aplica regra de Follow(Head) pertence a Follow(N) de forma recursiva
  # pelas dependencias rastreadas pela função trackHeadToBodyFollowDependencies
  def applyHeadToBodyFollow(
    self,
    target: str,
    origin: str,
    partialFollow: Dict[str, Set[str]],
    dependencies: Dict[str, Set[str]],
  ):
    old = partialFollow[target]
    new = partialFollow[target].union(partialFollow[origin])
    if (len(new.difference(old)) == 0):
      return
    partialFollow[target] = new
    dependents = dependencies[target]
    for dependent in dependents:
      self.applyHeadToBodyFollow(dependent, target, partialFollow, dependencies)

  def isDet(self) -> bool:
    #   Checa se uma GLC é determinante
    deterministic = self.isIndirectlyDeterministic()[0]
    return deterministic
  
  def isIndirectlyDeterministic(self) -> Tuple[bool, Dict[str, List[str]]]:
    #   Checa se uma GLC é determinante DIRETA E INDIRETAMENTE
    #   Retorna uma tupla com o resultado booleano e a estrutura
    # de dados que nos diz com que símbolo terminal começa cada produção
    deterministic, startsWithDirectly = self.isDirectlyDeterministic()
    startsWithIndirectly: Dict[str, List[str]] = startsWithDirectly
    if(not deterministic):
      deterministic = False
    for head in self.productions:
      for production in self.productions.get(head):
        firstSymbol = production[0]
        if(firstSymbol in self.terminals):
          continue
        if(head not in startsWithIndirectly):
          startsWithIndirectly[head] = [firstSymbol]
        else:
          if(firstSymbol in startsWithIndirectly[head]):
            deterministic = False
          startsWithIndirectly[head].append(firstSymbol)
    allFirstSymbols = set()
    for firstProductionList in startsWithIndirectly.values():
      for symbol in firstProductionList:
        allFirstSymbols.add(symbol)
    finished: bool = True
    for nTerminal in self.nTerminals:
      if(nTerminal in allFirstSymbols):
        finished = False
    timesAttempted = 0
    while((not finished) and (timesAttempted <= len(self.productions.items()))):
      timesAttempted += 1
      for head in startsWithIndirectly:
        for symbol in startsWithIndirectly[head]:
          if(symbol in self.nTerminals):
            startsWithIndirectly[head].remove(symbol)
            for newSymbol in startsWithIndirectly[symbol]:
              if(newSymbol in startsWithIndirectly[head]):
                deterministic = False
            startsWithIndirectly[head].extend(startsWithIndirectly[symbol])
            
      allFirstSymbols = set()
      for firstProductionList in startsWithIndirectly.values():
        for symbol in firstProductionList:
          allFirstSymbols.add(symbol)
      finished: bool = True
      for nTerminal in self.nTerminals:
        if(nTerminal in allFirstSymbols):
          finished = False
    
    
    return deterministic, startsWithIndirectly
    #for i in range(len(self.productions.items())):

  
  def isDirectlyDeterministic(self) -> Tuple[bool, Dict[str, List[str]]]:
    #   Retorna uma tupla do tipo (bool, Dict[str,List[str]])
    #   Esta tupla nos diz se é diretamente deterministica ou não, e nos
    # dá a estrutura com os terminais iniciais de cada uma das cabeças de produção (apenas diretamente) e com repetição onde há não determinismo
    startsWith: Dict[str, List[str]] = {}
    boolAnswer: bool = True
    for head in self.productions:
      for production in self.productions.get(head):
        # Para cada cabeça de produção, pegamos cada uma das produções e checamos se o seu primeiro símbolo é terminal
        first = production[0]
        if(first in self.terminals):
          # Se o primeiro símbolo for terminal, checamos se já houve outra produção da mesma cabeça que começa com o mesmo símbolo
          if(head not in startsWith):
            startsWith[head] = [first]
          else:
            if(first in startsWith[head]):
              boolAnswer = False
            startsWith[head].append(first)
    return boolAnswer, startsWith
  
  def determinize(self):
    # Determiniza uma GR
    attempts = 0
    while(not self.isIndirectlyDeterministic()[0] and attempts <= 10):
      attempts += 1
      self.removeDirectNonDeterminism()
      self.removeIndirectNonDeterminism()
    if(not self.isIndirectlyDeterministic()[0]):
      print("--------------------------------------------------")
      print("A DETERMINIZAÇÃO ENTROU EM LOOP QUANDO ESTAVA NA")
      print("GRAMÁTICA ACIMA")
      print("--------------------------------------------------")
      exit(-1)
  
  def removeDirectNonDeterminism(self):
    # Remove não-determinismo direto da gramática
    deterministic, startsWith = self.isDirectlyDeterministic()
    if(deterministic):
      return
    for head, firstTerminals in startsWith.items():
      repeatedList = getRepeatedElementsOfAList(firstTerminals)
      for repeated in repeatedList:
        newState = head
        while(newState in self.nTerminals):
          newState += "'"
        self.nTerminals.append(newState)
        removedProductions: List[str] = []
        for production in self.productions[head]:
          if(production[0] == repeated):
            removedProductions.append(production)
        for index,production in enumerate(removedProductions):
          self.productions[head].remove(production)
          if(removedProductions[index] == repeated):
            removedProductions[index] = '&'
            continue
          removedProductions[index] = production[1:len(production)]
        for production in removedProductions:
          if(newState not in self.productions):
            self.productions[newState] = [production]
          else:
            self.productions[newState].append(production)
        self.productions[head].append(repeated+newState)

  def removeIndirectNonDeterminism(self):
    # Remove não-determinismo indireto da gramática
    deterministic, startsWith = self.isIndirectlyDeterministic()
    if(deterministic):
      return
    for head, firstTerminals in startsWith.items():
      repeatedList: List[str] = getRepeatedElementsOfAList(firstTerminals)
      if(len(repeatedList) == 0):
        continue
      # Cabeça problemática
      for repeated in repeatedList:
        removedProductions: List[str] = []
        attempts = 0
        for production in self.productions[head]:
          firstSymbol = production[0]
          attempts += 1
          if(attempts>=50):
            print("--------------------------------------------------")
            print("A DETERMINIZAÇÃO ENTROU EM LOOP")
            print("--------------------------------------------------")
            exit(-1)
          if(firstSymbol in startsWith):
            if(repeated in startsWith[firstSymbol]):
              # Pegar as producoes de firstSymbol e jogar pras de Head
              #self.productions[head].extend(self.productions[firstSymbol])
              removedProductions.append(production)
              for producaoDeFirstSymbol in self.productions[firstSymbol]:
                novaProducao = producaoDeFirstSymbol+production[1:len(production)]
                if((novaProducao != "&") and ("&" in novaProducao)):
                  novaProducao = novaProducao.replace("&",'')
                if(novaProducao in self.productions[head]):
                  continue
                self.productions[head].append(novaProducao)
        for production in removedProductions:
          self.productions[head].remove(production)

  def LL1Table(self):
    
    table: Dict[str, Dict[str,str]] = {}
    first = self.first()
    follow = {
      'E': {"$"},
      "Y": {"$"},
      "T": {"$","+"},
      "X": {"$","+"},
      "F": {"$","+","*"}
    }
    for nTerminal in self.nTerminals:
      table[nTerminal] = {}
    for nTerminal in self.nTerminals:
        for production in self.productions[nTerminal]:
          pass
  def __str__(self):
    productions = ''
    for head, body in self.productions.items():
      productions += f"\n{head} {' '.join(body)}"
    return (
      "GR\n"
      f"{','.join(self.terminals)}\n"
      f"{','.join(self.nTerminals)}\n"
      f"{self.initial}"
      f"{productions}"
    )