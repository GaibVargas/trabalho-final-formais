from Node import *

class Arvore:
    nodo_raiz = None
    folhas = []

    def __init__(self):
        pass

    def set_nodo_raiz(self, novo_nodo_raiz):
        self.nodo_raiz = novo_nodo_raiz

    def get_nodo_raiz(self):
        return self.nodo_raiz

    def get_em_ordem(self):
        return self.nodo_raiz.em_ordem('')

    def costura_arvore(self):
        stack = [Nodo('$')]
        self.nodo_raiz.costura_nodo(stack)
        
    def numerar_folhas(self):
        self.folhas = []
        self.nodo_raiz.numerar_folhas(self.folhas)
        return self.folhas

    def composicao_da_raiz(self):
        composicao = {}
        self.nodo_raiz.descer(composicao)
        return composicao
