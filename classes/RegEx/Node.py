class Nodo:
    valor = None
    folha = None
    prioridade_operador = None
    filho_esquerdo = None
    filho_direito = None
    costura = None

    def __init__(self, valor, prioridade=0, folha=False):
        self.valor = valor
        self.prioridade_operador = prioridade
        self.folha = folha

    def set_valor(self, valor):
        self.valor = valor

    def get_valor(self):
        return self.valor

    def eh_folha(self):
        return self.folha

    def set_filho_esquerdo(self, novo_filho_esquerdo):
        self.filho_esquerdo = novo_filho_esquerdo

    def get_filho_esquerdo(self):
        return self.filho_esquerdo

    def set_filho_direito(self, novo_filho_direito):
        self.filho_direito = novo_filho_direito

    def get_filho_direito(self):
        return self.filho_direito

    def set_costura(self, nodo_costurado):
        self.costura = nodo_costurado

    def get_costura(self):
        if self.costura is not None:
            return self.costura
        else:
            return self.filho_direito.get_costura()

    def em_ordem(self, expressao):
        if self.filho_esquerdo is not None:
            if self.filho_esquerdo.prioridade_operador > self.prioridade_operador:
                expressao += '('
            expressao = self.filho_esquerdo.em_ordem(expressao)
            if self.filho_esquerdo.prioridade_operador > self.prioridade_operador:
                expressao += ')'
        if self.valor != '.':
            expressao += self.valor
        if self.filho_direito is not None:
            if self.filho_direito.prioridade_operador > self.prioridade_operador:
                expressao += '('
            expressao = self.filho_direito.em_ordem(expressao)
            if self.filho_direito.prioridade_operador > self.prioridade_operador:
                expressao += ')'
        return expressao

    def costura_nodo(self, stack):
        if self.filho_esquerdo is not None:
            stack.append(self)
            self.filho_esquerdo.costura_nodo(stack)
            stack.pop()

        if self.filho_direito is None:
            self.costura = stack[-1]
        else:
            self.filho_direito.costura_nodo(stack)

    def numerar_folhas(self, lista):
        if self.filho_esquerdo is not None:
            self.filho_esquerdo.numerar_folhas(lista)

        self.numerar_folha(lista)

        if self.filho_direito is not None:
            self.filho_direito.numerar_folhas(lista)

    def numerar_folha(self, lista):
        pass

    def descer(self, composicao):
        pass

    def subir(self, composicao):
        pass

    def str(self):
        return 'Nodo(\'' + self.get_valor() + '\')'
