########################################
# tabela de simbolos
########################################

class Simbolo:
    def __init__(self, nome, tipo, decl):
        self.nome = nome
        self.escopo = 0
        self.tipo = tipo
        self.decl = decl           # linha da declaracao
        self.usos = []             # linhas onde e usado
        self.fim = None            # linha final (so para o main)

    def add_uso(self, linha):
        if not self.usos or self.usos[-1] != linha:   # nao repete a mesma linha
            self.usos.append(linha)

class TabelaSimbolos:
    def __init__(self):
        self.itens = {}

    def declarar(self, nome, tipo, decl):
        if nome in self.itens:
            return None
        self.itens[nome] = Simbolo(nome, tipo, decl)
        return self.itens[nome]

    def buscar(self, nome):
        return self.itens.get(nome)

########################################
# tabela de codigos
########################################

class Estrutura:
    # uma linha da tabela: b1 e b2 = [linha inicio, linha fim]
    def __init__(self, nome):
        self.nome = nome
        self.b1 = None
        self.b2 = None

########################################
# saida das tabelas
########################################

def _tabela(titulo, cab, linhas):
    larg = [max([len(cab[i])] + [len(str(l[i])) for l in linhas]) for i in range(len(cab))]
    fmt = ' | '.join('{:<%d}' % w for w in larg)
    out = ['=== ' + titulo + ' ===', fmt.format(*cab), '-+-'.join('-' * w for w in larg)]
    return '\n'.join(out + [fmt.format(*[str(x) for x in l]) for l in linhas])

def _bl(b):
    if b is None:
        return '-', '-'
    return b[0], ('?' if b[1] is None else b[1])

def tabela_simbolos(tab):
    linhas = []
    for s in tab.itens.values():
        usos = ', '.join(str(u) for u in s.usos)
        if s.fim is not None:
            usos = 'fim ' + str(s.fim)
        linhas.append((s.nome, s.escopo, s.tipo, s.decl, usos))
    return _tabela('TABELA DE SÍMBOLOS', ['Identificador', 'Escopo', 'Tipo', 'Declaração', 'Usos (ou fim)'], linhas)

def tabela_codigos(estruturas):
    linhas = []
    for e in estruturas:
        linhas.append((e.nome,) + _bl(e.b1) + _bl(e.b2))
    return _tabela('TABELA DE CÓDIGOS', ['Comando', 'Início Bloco1', 'Fim Bloco1', 'Início Bloco2', 'Fim Bloco2'], linhas)
