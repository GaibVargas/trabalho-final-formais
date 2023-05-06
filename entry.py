import sys
from AF import AF

def readAF(content):
  alphabet, states, initial, finals, *transitions = content
  machine = AF(
    alphabet.strip().split(','),
    states.strip().split(','),
    initial.strip(),
    finals.strip().split(','),
    list(map(lambda x: x.strip(), transitions))
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
