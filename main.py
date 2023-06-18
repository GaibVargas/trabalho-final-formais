import sys
from classes.Parser import Parser
from utils.utils import archivePrint

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
main()
