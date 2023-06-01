from Node import Nodo
from enums import *

class NodoUniao(Nodo):
    def __init__(self):
        super(NodoUniao, self).__init__(Operacao.UNIAO.value, prioridade=prioridade(Operacao.UNIAO))

    def descer(self, composicao):
        composicao = self.get_filho_esquerdo().descer(composicao)
        composicao = self.get_filho_direito().descer(composicao)
        return composicao

    def subir(self, composicao):
        composicao = self.get_filho_direito().get_costura().subir(composicao)
        return composicao
