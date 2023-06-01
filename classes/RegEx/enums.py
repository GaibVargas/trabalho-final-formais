from enum import Enum

class Operacao(Enum):
    UNIAO = '|'
    CONCATENACAO = '.'
    FECHO = '*'
    OPCIONAL = '?'

prioridades = {
    Operacao.UNIAO: 2,
    Operacao.CONCATENACAO: 1,
    Operacao.FECHO: 0,
    Operacao.OPCIONAL: 0
}

def prioridade(operacao):
    return prioridades[operacao]
