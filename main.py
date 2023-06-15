import sys
from classes.Parser import Parser

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

def readFile(fileName):
  with open(fileName, 'r') as file:
    fileType, *content = file.readlines()
    if (fileType.strip() == 'AF'):
      return readAF(content)
    if (fileType.strip() == 'GR'):
      return readGR(content)
    print('Tipo de arquivo desconhecido')

def AFPrint():
  fileName = sys.argv[2]
  response = readFile(fileName)
  print(response)

def GRPrint():
  fileName = sys.argv[2]
  response = readFile(fileName)
  print(response)

def GRToAF():
  fileName = sys.argv[2]
  grammar = readFile(fileName)
  af = grammar.parseToAF()
  print(grammar)
  print(af)

def AFToGR():
  fileName = sys.argv[2]
  af = readFile(fileName)
  grammar = af.parseToGR()
  print(af)
  print(grammar)

def AFMin():
  fileName = sys.argv[2]
  af = readFile(fileName)
  af.minimize()
  print(af)

def AFDet():
  fileName = sys.argv[2]
  af = readFile(fileName)
  af.determinize()
  print(af)

def AFTest():
  fileName = sys.argv[2]
  word = ''
  if (len(sys.argv) >= 4):
    word = sys.argv[3]

  af = readFile(fileName)
  # TODO: determinizar antes
  #af.determinize()
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
  print(union)

def AFIntersection():
  fileOneName = sys.argv[2]
  fileTwoName = sys.argv[3]
  afOne = readFile(fileOneName)
  afTwo = readFile(fileTwoName)
  afComplementOne = afOne.complement()
  afComplementTwo = afTwo.complement()
  unionOfComplement = afComplementOne.union(afComplementTwo)
  unionOfComplement.determinize()
  print(unionOfComplement.complement())

def main():
  function = sys.argv[1]
  if function == "AF-print":
    return AFPrint()
  if function == "GR-print":
    return GRPrint()
  if function == "GR-AF":
    return GRToAF()
  if function == "AF-GR":
    return AFToGR()
  if function == "AF-min":
    return AFMin()
  if function == "AF-test":
    return AFTest()
  if function == "LL":
    return LL()
  if function == "AF-det":
    return AFDet()
  if function == "AF-union":
    return AFUnion()
  if function == "AF-intersection":
    return AFIntersection()

main()
