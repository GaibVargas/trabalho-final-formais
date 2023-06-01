from Node import *
from enums import *

class NodoConcatenacao(Nodo):
    def __init__(self):
        super(NodoConcatenacao, self).__init__(Operacao.CONCATENACAO.value, prioridade=prioridade(Operacao.CONCATENACAO))

    def descer(self, composicao):
        composicao = self.get_filho_esquerdo().descer(composicao)
        return composicao

    def subir(self, composicao):
        composicao = self.get_filho_direito().descer(composicao)
        return composicao
