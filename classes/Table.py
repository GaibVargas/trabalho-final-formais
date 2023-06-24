from typing import Dict
from tabulate import tabulate

class Table:
  def __init__(self, table: Dict[str, Dict[str,str]]):
    self.table = table
  
  def __str__(self) -> str:
    terminals = set()
    nTerminals = list(self.table.keys())
    for nTerminal in nTerminals:
      terminalsOfHead = (list(self.table[nTerminal].keys()))
      for terminalOfHead in terminalsOfHead:
        terminals.add(terminalOfHead)
    terminals = list(terminals)
    rows = []
    for nTerminal in nTerminals:
      row = [nTerminal]
      for terminal in terminals:
        try:
          row.append(self.table[nTerminal][terminal])
        except:
          row.append('/')
      rows.append(row)


    return tabulate(rows, terminals, tablefmt='grid')