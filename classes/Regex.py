import string
from RegEx.Element import Element
from RegEx.ConcatenationNode import NodoConcatenacao
from RegEx.ClosureNode import NodoFecho
from RegEx.LeafNode import NodoFolha
from RegEx.OptionalNode import NodoOpcional
from RegEx.UnionNode import NodoUniao
from RegEx.Tree import Arvore
from AF import AF
from State import State
from RegEx.enums import Operacao, prioridade

class ExpressaoRegular(Element):
    arvore = None

    def __init__(self, nome):
        super(ExpressaoRegular, self).__init__(nome)

    # Recebe a expressão como texto e chama a função para gerar e armazenar a árvore correspondente
    def ler(self, expressao):
        self.gerar_arvore(expressao)

    # Retorna a expressão regular como texto
    def to_string(self):
        return self.arvore.get_em_ordem()

    # Gera a árvore a partir da expressão regular em texto
    def gerar_arvore(self, expressao):
        self.arvore = Arvore()
        expressao = self.preparar_expressao(expressao)
        if self.verificar_validade(expressao):
            self.arvore.set_nodo_raiz(self.gerar_nodo(expressao))
            self.arvore.costura_arvore()
            self.arvore.numerar_folhas()
        try:
            self.verificar_validade(self.to_string())
        except:
            raise Exception

    # Gera a árvore/sub-árvore a partir da expressão/sub-expressão regular dada
    def gerar_nodo(self, expressao):
        subexpressao = self.remover_parenteses_externos(expressao)
        if len(subexpressao) == 1:
            return NodoFolha(subexpressao)
        else:
            operador_div = None
            prioridade_div = -1
            posicao_div = None
            parenteses_abertos = 0
            for i in range(0, len(subexpressao)):
                char = subexpressao[i]
                if char == '(':
                    parenteses_abertos += 1
                elif char == ')':
                    parenteses_abertos -= 1
                elif parenteses_abertos == 0:
                    if char == '|' and prioridade_div < 2:
                        operador_div = Operacao.UNIAO
                        prioridade_div = prioridade(operador_div)
                        posicao_div = i
                    if char == '.' and prioridade_div < 1:
                        operador_div = Operacao.CONCATENACAO
                        prioridade_div = prioridade(operador_div)
                        posicao_div = i
                    if char == '*' and prioridade_div < 0:
                        operador_div = Operacao.FECHO
                        prioridade_div = prioridade(operador_div)
                        posicao_div = i
                    if char == '?' and prioridade_div < 0:
                        operador_div = Operacao.OPCIONAL
                        prioridade_div = prioridade(operador_div)
                        posicao_div = i
            nodo = None
            if operador_div == Operacao.UNIAO:
                nodo = NodoUniao()
                nodo.set_filho_esquerdo(self.gerar_nodo(subexpressao[0:posicao_div]))
                nodo.set_filho_direito(self.gerar_nodo(subexpressao[posicao_div + 1:]))
            elif operador_div == Operacao.CONCATENACAO:
                nodo = NodoConcatenacao()
                nodo.set_filho_esquerdo(self.gerar_nodo(subexpressao[0:posicao_div]))
                nodo.set_filho_direito(self.gerar_nodo(subexpressao[posicao_div + 1:]))
            elif operador_div == Operacao.FECHO:
                nodo = NodoFecho()
                nodo.set_filho_esquerdo(self.gerar_nodo(subexpressao[0:posicao_div]))
            else:
                nodo = NodoOpcional()
                nodo.set_filho_esquerdo(self.gerar_nodo(subexpressao[0:posicao_div]))
            return nodo

    # Verifica se uma expressão é valida
    def verificar_validade(self, expressao):
        if not expressao:
            raise Exception
        chars_validos = string.ascii_lowercase + string.digits + '|.*?()'
        nivel_parenteses = 0
        char_anterior = ' '
        i_real = 0
        for i in range(0, len(expressao)):
            char = expressao[i]
            if char in chars_validos:
                if i > 1:
                    if char_anterior in '|.(' and char in '|.*?)':
                        raise Exception
                    elif char_anterior in '*?' and char in '*?':
                        raise Exception
                if char == '(':
                    nivel_parenteses += 1
                elif char == ')':
                    nivel_parenteses -= 1
                    if nivel_parenteses < 0:
                        raise Exception
                elif char == '.':
                    i_real -= 1
            else:
                raise Exception
            char_anterior = char
            i_real += 1
        if nivel_parenteses > 0:
            raise Exception
        return True

    # Prepara a expressão para o algoritmo de construção da árvore
    def preparar_expressao(self, expressao):
        # Elimina espaços em branco
        expressao = ''.join(expressao.split())
        # Expõe concatenações
        expressao = self.expor_concatenacoes_implicitas(expressao)
        return expressao

    # Expõe concatenações implícitas em uma expressão regular
    def expor_concatenacoes_implicitas(self, expressao):
        add_expressao = expressao
        char_anterior = ' '
        concats_adicionadas = 0
        for i in range(0, len(expressao)):
            char = expressao[i]
            if (char_anterior.isalnum() or (char_anterior in ')*?')) and (char.isalnum() or char == '('):
                add_expressao = add_expressao[:i+concats_adicionadas] + '.' + add_expressao[i+concats_adicionadas:]
                concats_adicionadas += 1
            char_anterior = char

        return add_expressao

    # Remove parênteses redundantes nas extremidades de uma expressão
    def remover_parenteses_externos(self, expressao):
        parenteses_encontrados = 0
        nivel = 0
        inicio = True
        i = 0
        comprimento_expr = len(expressao)
        while i < comprimento_expr - parenteses_encontrados:
            char = expressao[i]
            if char == '(':
                nivel += 1
                if inicio:
                    parenteses_encontrados = nivel
            else:
                inicio = False
                if char == ')':
                    nivel -= 1
                    parenteses_encontrados = min(parenteses_encontrados, nivel)
            i += 1
        return expressao[parenteses_encontrados:comprimento_expr - parenteses_encontrados]

    # Transforma esta expressão regular em um autômato finito
    def obter_AF_equivalente(self):
        folhas = self.arvore.numerar_folhas()
        obter_composicao = {}
        obter_estado = {}
        i = 0

        prefixo_do_estado = 'Q'
        estado_inicial = State(prefixo_do_estado + str(i))

        composicao_da_raiz = self.arvore.composicao_da_raiz()
        obter_composicao[estado_inicial] = composicao_da_raiz
        obter_estado[self.obter_composicao_como_chave(composicao_da_raiz)] = estado_inicial

        estados_do_automato = [estado_inicial]
        estados_incompletos = [estado_inicial]
        estados_de_aceitacao = []
        alfabeto = []
        i += 1
        while len(estados_incompletos) > 0:
            estado_atual = estados_incompletos.pop(0)
            composicao_atual = obter_composicao[estado_atual]
            for simbolo in composicao_atual:
                if simbolo != '$':
                    novo_estado = State(prefixo_do_estado + str(i))
                    i += 1
                    nova_composicao = {}
                    if simbolo not in alfabeto:
                        alfabeto.append(simbolo)
                    for numero_folha in composicao_atual[simbolo]:
                        folhas[numero_folha].subir(nova_composicao)
                    obter_composicao[novo_estado] = nova_composicao
                    nova_composicao_como_chave = self.obter_composicao_como_chave(nova_composicao)
                    if nova_composicao_como_chave not in obter_estado:
                        obter_estado[nova_composicao_como_chave] = novo_estado
                        estados_do_automato.append(novo_estado)
                        estados_incompletos.append(novo_estado)
                    else:
                        novo_estado = obter_estado[nova_composicao_como_chave]
                    estado_atual.addTransition(simbolo, novo_estado)
                else:
                    estados_de_aceitacao.append(estado_atual)
        automato = AF(alfabeto, estados_do_automato, estado_inicial, estados_de_aceitacao)
        return automato

    # Transforma a composição de um estado em um valor único
    def obter_composicao_como_chave(self, composicao):
        id_nova_composicao = []
        for simb in composicao:
            par = (simb, tuple(sorted(list(composicao[simb]))))
            id_nova_composicao.append(par)
        return tuple(id_nova_composicao)
