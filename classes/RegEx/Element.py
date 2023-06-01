class Elemento:
    nome = None
    tipo = None

    def __init__(self, nome):
        self.nome = nome

    def get_nome(self):
        return self.nome

    def set_nome(self, novo_nome):
        self.nome = novo_nome

    def ler(self, expressao):
        pass

    def to_string(self):
        return ''