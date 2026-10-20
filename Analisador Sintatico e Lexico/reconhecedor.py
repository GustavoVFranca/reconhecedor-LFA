from lexer import *
from tabelas import *
########################################
# parte dos nodes
########################################

class numberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'

class binOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node} {self.op_tok} {self.right_node})'
    
class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

    def __repr__(self):
        return f'({self.op_tok} {self.node})'

class node:
    # node generico para os comandos: (TIPO filho1 filho2 ...)
    def __init__(self, tipo, *filhos):
        self.tipo = tipo
        self.filhos = filhos

    def __repr__(self):
        return '(' + self.tipo + ' ' + ' '.join(str(f) for f in self.filhos) + ')'

########################################
# resultado parser
######################################## 

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node

        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self 

########################################
# parte do parser
########################################
class parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.tipo != TT_COMMENT]   # comentarios sao ignorados
        self.tok_idx = -1
        self.simbolos = TabelaSimbolos()
        self.codigos = []
        self.contadores = {'IF': 0, 'WHILE': 0}
        self.advance()

    def advance(self): 
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok 

    def espera(self, res, tipo, descricao):
        # se o token atual for o esperado consome e devolve, senao registra o erro em res
        if self.current_tok.tipo == tipo:
            tok = self.current_tok
            res.register(self.advance())
            return tok
        idx = min(self.tok_idx, len(self.tokens) - 1)
        anterior = self.tokens[idx - 1] if idx > 0 else self.current_tok
        if self.current_tok.tipo != TT_EOF and anterior.linha < self.current_tok.linha:
            # o que falta (ex: ';') devia estar no fim da linha anterior
            res.failure(invalidSyntaxError(
                anterior.pos_start, anterior.pos_end,
                "Esperado " + descricao + " depois de '" + anterior.lexema + "'"
            ))
        else:
            res.failure(invalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Esperado " + descricao + ", encontrado '" + self.current_tok.lexema + "'"
            ))

    def parse(self):
        res = self.principal()
        if not res.error and self.current_tok.tipo != TT_EOF:
            return res.failure(invalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Token inesperado"
            ))
        return res

    ########################################
    # main, blocos e comandos
    ########################################
    def principal(self):
        res = ParseResult()
        tok = self.espera(res, TT_MAIN, "'main'")
        if res.error: return res

        s = self.simbolos.declarar('main', 'principal', tok.linha)
        est = Estrutura('PRINCIPAL')
        est.b1 = [tok.linha, None]
        self.codigos.append(est)

        corpo = res.register(self.bloco(est, 'b2'))
        if res.error: return res

        est.b1[1] = s.fim = est.b2[1]
        return res.success(node('MAIN', corpo))

    def bloco(self, est=None, attr=None):
        res = ParseResult()
        lb = self.espera(res, TT_LBRACE, "'{'")
        if res.error: return res

        b = [lb.linha, None]
        if est is not None:
            setattr(est, attr, b)

        comandos = []
        while self.current_tok.tipo not in (TT_RBRACE, TT_EOF):
            cmd = res.register(self.comando())
            if res.error: return res
            comandos.append(cmd)

        rb = self.espera(res, TT_RBRACE, "'}' (para fechar o '{' da linha " + str(lb.linha) + ")")
        if res.error: return res
        b[1] = rb.linha
        return res.success(node('BLOCO', *comandos))

    def comando(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.tipo in TIPOS_DADO:
            return self.declaracao()

        elif tok.tipo == TT_IDENTIFIER:
            atrib = res.register(self.atribuicao())
            if res.error: return res
            self.espera(res, TT_SEMI, "';'")
            if res.error: return res
            return res.success(atrib)

        elif tok.tipo == TT_IF:
            return self.cmd_if()

        elif tok.tipo == TT_WHILE:
            return self.cmd_while()

        elif tok.tipo == TT_PRINT:
            return self.cmd_print()

        elif tok.tipo == TT_LBRACE:
            return self.bloco()

        return res.failure(invalidSyntaxError(tok.pos_start, tok.pos_end, "Comando inválido: '" + tok.lexema + "'"))

    def declaracao(self):
        # tipo IDENT [= expr] {, IDENT [= expr]} ;
        res = ParseResult()
        tipo_tok = self.current_tok
        res.register(self.advance())

        itens = []
        while True:
            nome = self.espera(res, TT_IDENTIFIER, "um identificador")
            if res.error: return res

            inicial = None
            if self.current_tok.tipo == TT_ASSIGN:
                res.register(self.advance())
                inicial = res.register(self.or_expr())
                if res.error: return res

            if self.simbolos.declarar(nome.valor, tipo_tok.valor, nome.linha) is None:
                return res.failure(semanticError(
                    nome.pos_start, nome.pos_end, "Variável '" + nome.valor + "' já declarada"
                ))
            itens.append(node('VAR', nome, inicial))

            if self.current_tok.tipo != TT_COMMA:
                break
            res.register(self.advance())

        self.espera(res, TT_SEMI, "';'")
        if res.error: return res
        return res.success(node('DECL', tipo_tok, *itens))

    def atribuicao(self):
        # IDENT = expr   (sem o ';')
        res = ParseResult()
        nome = self.espera(res, TT_IDENTIFIER, "um identificador")
        if res.error: return res
        self.espera(res, TT_ASSIGN, "'=' após '" + nome.valor + "'")
        if res.error: return res

        erro = self.usar_variavel(nome)
        if erro: return res.failure(erro)

        valor = res.register(self.or_expr())
        if res.error: return res
        return res.success(node('ASSIGN', nome, valor))

    def condicao(self):
        # ( expr )
        res = ParseResult()
        self.espera(res, TT_LPAREN, "'('")
        if res.error: return res
        cond = res.register(self.or_expr())
        if res.error: return res
        self.espera(res, TT_RPAREN, "')'")
        if res.error: return res
        return res.success(cond)

    def nova_estrutura(self, prefixo):
        self.contadores[prefixo] += 1
        est = Estrutura(prefixo + str(self.contadores[prefixo]))
        self.codigos.append(est)
        return est

    def cmd_if(self):
        res = ParseResult()
        res.register(self.advance())
        est = self.nova_estrutura('IF')

        cond = res.register(self.condicao())
        if res.error: return res
        then_node = res.register(self.bloco(est, 'b1'))
        if res.error: return res

        else_node = None
        if self.current_tok.tipo == TT_ELSE:
            res.register(self.advance())
            est.nome = est.nome + ' / ' + est.nome.replace('IF', 'ELSE')
            else_node = res.register(self.bloco(est, 'b2'))
            if res.error: return res

        return res.success(node('IF', cond, then_node, else_node))

    def cmd_while(self):
        res = ParseResult()
        res.register(self.advance())
        est = self.nova_estrutura('WHILE')

        cond = res.register(self.condicao())
        if res.error: return res
        corpo = res.register(self.bloco(est, 'b1'))
        if res.error: return res
        return res.success(node('WHILE', cond, corpo))

    def cmd_print(self):
        # print ( expr {, expr} ) ;
        res = ParseResult()
        res.register(self.advance())
        self.espera(res, TT_LPAREN, "'('")
        if res.error: return res

        args = []
        while True:
            arg = res.register(self.or_expr())
            if res.error: return res
            args.append(arg)
            if self.current_tok.tipo != TT_COMMA:
                break
            res.register(self.advance())

        self.espera(res, TT_RPAREN, "')'")
        if res.error: return res
        self.espera(res, TT_SEMI, "';'")
        if res.error: return res
        return res.success(node('PRINT', *args))

    def usar_variavel(self, tok):
        s = self.simbolos.buscar(tok.valor)
        if s is None:
            return semanticError(tok.pos_start, tok.pos_end, "'" + tok.valor + "' não foi declarado")
        s.add_uso(tok.linha)

    ########################################
    # expressoes (precedencia: || < && < comparacao < + - < * / < unario)
    ########################################
    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.tipo in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor =  res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.tipo in (TT_INTEGER, TT_REAL):
            res.register(self.advance())
            return res.success(numberNode(tok))

        elif tok.tipo == TT_TEXT:
            res.register(self.advance())
            return res.success(node('TEXTO', tok))

        elif tok.tipo == TT_IDENTIFIER:
            erro = self.usar_variavel(tok)
            if erro: return res.failure(erro)
            res.register(self.advance())
            return res.success(node('VAR', tok))
        
        elif tok.tipo == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.or_expr())
            if res.error: return res
            self.espera(res, TT_RPAREN, "')'")
            if res.error: return res
            return res.success(expr)
        
        return res.failure(invalidSyntaxError(
            tok.pos_start, tok.pos_end, "Esperado número, texto, identificador ou '(', encontrado '" + tok.lexema + "'"
        ))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self): 
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def comp_expr(self):
        return self.bin_op(self.expr, (TT_LESS, TT_GREATER, TT_LESS_EQ, TT_GREATER_EQ, TT_EQ, TT_NOT_EQ))

    def and_expr(self):
        return self.bin_op(self.comp_expr, (TT_AND,))

    def or_expr(self):
        return self.bin_op(self.and_expr, (TT_OR,))

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        while self.current_tok.tipo in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = binOpNode(left, op_tok, right)

        return res.success(left)
########################################
# rodar
########################################   
def compilar(fn, texto):
    lexer = Lexer(fn, texto)
    tokens, error = lexer.make_tokens()
    if error:
        return tokens, None, None, None, error

    p = parser(tokens)
    ast = p.parse()

    return tokens, ast.node, p.simbolos, p.codigos, ast.error

def run(fn, texto):
    tokens, ast, simbolos, codigos, error = compilar(fn, texto)
    return ast, error