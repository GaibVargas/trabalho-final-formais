import sys
from classes.Parser import Parser

def readAF(content):
  alphabet, states, initial, finals, *transitions = content
  parser = Parser()
  machine = parser.textToAF(
    alphabet,
    states,
    initial,
    finals,
    transitions
  )
  print(machine)

def readFile(fileName):
  with open(fileName, 'r') as file:
    fileType, *content = file.readlines()
    if (fileType.strip() == 'AF'):
      return readAF(content)
    print('sla')

def main():
  fileName = sys.argv[1]
  readFile(fileName)

main()
