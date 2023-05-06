# Formato de entrada
- primeira linha identificação do arquivo: GR, AF, ER
- entradas
    - AFND e AFD
        - alfabeto
        - estados (1 letra maiuscula)
        - inicial
        - finais
        - transição
            - estado alfabeto estado
    - GR
        - N aB a

# Estrutura
- OO pra manter organização
- Estado
    - id(nome)
    - transições
        - dicionário: { alfabeto -> [id] }
    - isFinal
- Máquina (vai precisar respeitar um contrato)
    - estados: Estado
    - inicial: id
    - getStateById(id): Estado (talvez não fique aqui)
    - validateSentence(string): boolean
    - print()
- Gramática
    - print de produções
    - segue a quadrupla
- Operação
    - ou, e, minimização

- Fazer por último, utilitário de linha de comando

# Entrada de cada exercício
a) recebe texto -> transformar texto em máquina -> determiniza produzindo máquina
b)
    1) recebe texto -> transforma texto em máquina -> gera gramática -> printa gramática
    2) recebe texto -> transforma texto em gramática -> gera AFND -> printa AFND
c) recebe texto -> transforma texto em máquina -> minimiza -> printa nova máquina
d) recebe 2 máquinas em texto -> transforma cada uma delas -> faz operação -> determiniza -> gera nova máquina e printa
e) recebe texto -> transforma texto máquina -> printa
f) recebe máquina texto e sentença -> transforma em máquina -> determiniza -> minimiza -> faz validação da sentença