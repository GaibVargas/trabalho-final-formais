# Como rodar o projeto
```
python main.py <função> [entries/<nome do arquivo>.txt]
```
### Exemplo
```
python main.py AF-GR entries/afd.txt
```

# Funções
- AF-print: recebe um arquivo do tipo AF e printa um AFND construído
- AF-GR: recebe um arquivo do tipo AF e printa gramática equivalente
- GR-AF: recebe um arquivo do tipo GR e printa AFND equivalente
- Af-min: recebe um arquivo do tipo AF e printa AFD semi-minimizado (falta calcular estados equivalentes)

# Organização do projeto
Pastas
- classes: Contém as classes do projeto
- entries: Contém arquivos testes de entrada
- util: Contém arquivos utilitários do projeto (funções que não se encaixam com a responsabilidade de alguma classe do sistema)

Arquivos
- main.py: Arquivo de entrada do sistema