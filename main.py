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

def main():
  function = sys.argv[1]
  if function == "AF-print":
    return AFPrint()
  if function == "GR-AF":
    return GRToAF()
  if function == "AF-GR":
    return AFToGR()

main()
