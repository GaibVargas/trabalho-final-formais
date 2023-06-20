from typing import Dict, List

class Table:
  def __init__(self, table: Dict[str, Dict[str,str]]):
    self.table = table
  
  def __str__(self) -> str:
    terminals = set()
    nTerminals = list(self.table.keys())
    saida = ""
    for nTerminal in nTerminals:
      terminalsOfHead = (list(self.table[nTerminal].keys()))
      for terminalOfHead in terminalsOfHead:
        terminals.add(terminalOfHead)
    primeiraLinha = "__|"
    for terminal in terminals:
      primeiraLinha += f" {terminal} "
    for nTerminal in nTerminals:
      saida += f"{nTerminal} |"
      for terminal in terminals:
        try:
          saida += f" {self.table[nTerminal][terminal]} "
        except:
          saida += f" / "
      saida += "\n"
    return (
      "TABELA\n"
      f"{primeiraLinha}\n"
      f"{saida}"

    )