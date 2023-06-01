from Node import *

class NodoFolha(Nodo):
    numero = None

    def __init__(self, valor):
        super(NodoFolha, self).__init__(valor, folha=True)

    def numerar_folha(self, lista):
        self.numero = len(lista)
        lista.append(self)

    def descer(self, composicao):
        if self.get_valor() not in composicao:
            composicao[self.get_valor()] = set()
        composicao[self.get_valor()].add(self.numero)
        return composicao

    def subir(self, composicao):
        if self.get_valor() == '$':
            composicao['$'] = set()
            composicao['$'].add(-1)
            return composicao

        composicao = self.get_costura().subir(composicao)
        return composicao
