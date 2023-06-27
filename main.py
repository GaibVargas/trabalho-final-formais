import sys
from classes.Parser import Parser
from classes.Table import Table
from classes.GR import GR
from utils.utils import archivePrint
from collections import OrderedDict

def readAF(content):
  alphabet, states, initial, finals, *transitions = content
  parser = Parser()
  return parser.textToAF(
    alphabet,
    states,
    initial,
    finals,
    transitions
  )

def readGR(content):
  terminals, nTerminals, initial, *productions = content
  parser = Parser()
  return parser.textToGR(
    terminals,
    nTerminals,
    initial,
    productions
  )

def formatInput(gr):
    productionsInDict = gr.productions
    mapOfProductions = OrderedDict()
    # key = non-terminal and value = productions with that non-terminal
    for key, value in productionsInDict.items():
        string_for_right_side = ""
        for i in range(len(value)):
            if (i != len(value) - 1):
                string_for_right_side += value[i] + " | "
            else:
                string_for_right_side += value[i]
        mapOfProductions[key.strip()] = string_for_right_side.strip()
    return mapOfProductions

def removeEpsilonAndPrepare(productions):
    prod = productions.copy()
    for key in prod:
        if '|' in prod[key]:
            split_array = prod[key].split('|')
            # Remove epsilon
            if '&' in split_array:
                split_array.remove('&')
            prod[key] = [x.strip() for x in split_array]
        else:
            prod[key] = [prod[key]]
    return prod

def eliminateIndirectRecursion(productions):
    i = 0
    j = 0
    for key, value in productions.items():
        # Remove indirect recursion
        for keyDic, valueDic in productions.items():
            if j > i:
                # Iterate in all sentences
                for sentence in valueDic:
                    if sentence[0] == key:
                        backup = productions[keyDic]
                        posToAdd = backup.index(sentence)
                        backup.remove(sentence)
                        posFixKey = sentence[1:]
                        # Add new values
                        toAdd = [x+posFixKey for x in value]
                        for x in toAdd:
                            backup.insert(posToAdd, x)
                        productions[keyDic] = backup
                    break
            j = j + 1
        j = 0
        i = i + 1
    return productions

def eliminateDirectRecursion(productions):
    dic_without_recursion = OrderedDict()
    for key, value in productions.items():
        isLeftRecursive = False
        for sentence in value:
            if sentence[0] == key:
                isLeftRecursive = True
        # No resursives, just copy the sentence
        if not isLeftRecursive:
            dic_without_recursion[key] = value
        else:
            # Is left recursive, remove the first symbol
            newKeyValue = key + "'"
            while newKeyValue in dic_without_recursion:
                newKeyValue = newKeyValue + "'"
            recursive_values = []
            not_recursive_values = []
            for sentence in value:
                if sentence[0] == key:
                    # A -> Aa 
                    recursive_values.append(sentence[1:] + newKeyValue)
                else:
                    # E -> ab | EC
                    # E -> abE'
                    not_recursive_values.append(sentence + newKeyValue)
            recursive_values.append("&")
            dic_without_recursion[key] = not_recursive_values
            dic_without_recursion[newKeyValue] = recursive_values
    return dic_without_recursion

def fixFirstProd(productions):
    first_value = list(productions)[-1]
    isLeftRecursive = False
    for sentence in productions[first_value]:
        if sentence[0] == first_value:
            isLeftRecursive = True
            break
    if isLeftRecursive:
        new_dic = productions.copy()
        # Is left recursive, remove the first symbol
        newKeyValue = first_value + "'"
        while newKeyValue in new_dic:
            newKeyValue = newKeyValue + "'"
        recursive_values = []
        not_recursive_values = []
        for sentence in productions[first_value]:
            if sentence[0] == first_value:
                # A -> Aa 
                recursive_values.append(sentence[1:] + newKeyValue)
            else:
                # E -> ab | EC
                # E -> abE'
                not_recursive_values.append(sentence + newKeyValue)
        recursive_values.append("&")
        new_dic[first_value] = not_recursive_values
        new_dic[newKeyValue] = recursive_values
        return new_dic
    else:
        return productions
# Final Function For Elimination of Left Recursion
def eliminateLeftRecursion(gr):
    productions = formatInput(gr)
    withouEpsilon = removeEpsilonAndPrepare(productions)
    withoutFirst = fixFirstProd(withouEpsilon)
    withoutIndirect = eliminateIndirectRecursion(withouEpsilon)
    withoutDirect = eliminateDirectRecursion(withoutIndirect)
    leftRecursive = True
    while leftRecursive:
        leftRecursive = False
        for key, value in withoutDirect.items():
            for val in value:
                if key == val[0]:
                    leftRecursive = True
                    break
        if leftRecursive:
            withoutFirst = fixFirstProd(withoutDirect)
            withoutIndirect = eliminateIndirectRecursion(withoutFirst)
            withoutDirect = eliminateDirectRecursion(withoutIndirect)
        else:
            # Fix Production 
            new_dic = {}
            for key, value in withoutDirect.items():
                value_to_add = []
                for val in value:
                    value_to_add.append(val.strip())
                new_dic[key] = value_to_add
            # TODO: Need to pass the dictionary into a string that the Parser can understand
            stringToParse = 'GR\n' # With Grammar and goes to another line for terminals -> non terminals -> initial terminal -> productions
            return readGR(stringToParse)


def readFile(fileName):
  with open(fileName, 'r') as file:
    fileType, *content = file.readlines()
    if (fileType.strip() == 'AF'):
      return readAF(content)
    if (fileType.strip() == 'GR'):
      return readGR(content)
    print('Tipo de arquivo desconhecido')

def GRToAF():
  fileName = sys.argv[2]
  grammar = readFile(fileName)
  af = grammar.parseToAF()
  archivePrint('af', af)

def AFToGR():
  fileName = sys.argv[2]
  af = readFile(fileName)
  grammar = af.parseToGR()
  archivePrint('gr', grammar)

def AFMin():
  fileName = sys.argv[2]
  af = readFile(fileName)
  af.minimize()
  archivePrint('af', af)

def AFDet():
  fileName = sys.argv[2]
  af = readFile(fileName)
  af.determinize()
  archivePrint('af', af)

def AFTest():
  fileName = sys.argv[2]
  word = ''
  if (len(sys.argv) >= 4):
    word = sys.argv[3]

  af = readFile(fileName)
  af.determinize()
  af.minimize()
  test = af.test(word)

  if (word == ''):
    word = 'Palavra vazia'
  testResult = 'Sim' if test else 'Não'
  print(f'"{word}" pertence a linguagem? {testResult}')

def LL():
  fileName = sys.argv[2]
  gr = readFile(fileName)
  first = gr.first()
  print(f'First: {first}')
  follow = gr.follow()
  print(f'Follow: {follow}')

def AFUnion():
  fileOneName = sys.argv[2]
  fileTwoName = sys.argv[3]
  afOne = readFile(fileOneName)
  afTwo = readFile(fileTwoName)
  union = afOne.union(afTwo)
  archivePrint('af', union)

def AFIntersection():
  fileOneName = sys.argv[2]
  fileTwoName = sys.argv[3]
  afOne = readFile(fileOneName)
  afTwo = readFile(fileTwoName)
  afComplementOne = afOne.complement()
  afComplementTwo = afTwo.complement()
  unionOfComplement = afComplementOne.union(afComplementTwo)
  unionOfComplement.determinize()
  archivePrint('af', unionOfComplement.complement())

def GLCisDet():
  fileName = sys.argv[2]
  glc = readFile(fileName)
  print(glc.isDet())

def GLCDet():
  fileName = sys.argv[2]
  glc = readFile(fileName)
  if(glc.isDet()):
    print("Esta gramática já é determinística")
    return 
  glc.determinize()
  archivePrint('glc', glc)
  
def LL1Table():
  fileName = sys.argv[2]
  glc = readFile(fileName)
  #   TODO: Tirar recursão, determinizar e checar intersecção de 
  # Firsts e Follows para cada um dos não-terminais
  table = Table(glc.LL1Table())
  print(table)
  
def main():
  function = sys.argv[1]
  if function == "AF-det":
    return AFDet()
  if function == "AF-GR":
    return AFToGR()
  if function == "GR-AF":
    return GRToAF()
  if function == "AF-min":
    return AFMin()
  if function == "AF-union":
    return AFUnion()
  if function == "AF-intersection":
    return AFIntersection()
  if function == "AF-test":
    return AFTest()
  if function == "LL":
    return LL()
  if function == "GLC-isDet":
    return GLCisDet()
  if function == "GLC-det":
    return GLCDet()
  if function == "LL1-table":
    return LL1Table()
main()
