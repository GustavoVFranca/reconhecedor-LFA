# Definição palavras reservadas

from unittest import result
from strings_with_arrows import * 
########################################
# tokens
########################################
TT_INT = 'INT'
TT_DOUBLE = 'DOUBLE'
TT_STRING = 'STRING' 
TT_VAR = 'VAR'   
TT_IF = 'IF'
TT_ELSE = 'ELSE'    
TT_WHILE = 'WHILE' 
TT_FOR = 'FOR'
TT_RETURN = 'RETURN'
TT_PRINT = 'PRINT'

# definição de operadores matemáticos
TT_PLUS = 'PLUS' # +
TT_MINUS = 'MINUS' # -
TT_DIV = 'DIV' # /
TT_MUL = 'MUL' # *
TT_POWER = 'POWER' # ^

# definição de operadores logicos
TT_LESS = 'LESS' # <
TT_GREATER = 'GREATER' # >
TT_LESS_EQ = 'LESS_EQ' # <=
TT_GREATER_EQ = 'GREATER_EQ' # >=
TT_EQ = 'EQ' # ==
TT_NOT_EQ = 'NOT_EQ' # !=  
TT_NOT = 'NOT' # !
TT_AND = 'AND' # &&
TT_OR = 'OR' # ||
TT_ASSIGN = 'ASSIGN' # =

# definição de separadores
TT_LPAREN = 'LPAREN' # (
TT_RPAREN = 'RPAREN' # )
TT_LBRACE = 'LBRACE' # {
TT_RBRACE = 'RBRACE' # }
TT_SEMI = 'SEMI' # ;
TT_COMMA = 'COMMA' # ,  

# definição comentario
TT_COMMENT = 'COMMENT' # //

# reconhecer tokens de variaveis, numeros e texto
TT_IDENTIFIER = 'IDENTIFIER'
TT_REAL = 'REAL'
TT_INTEGER = 'INTEGER'
TT_TEXT = 'TEXT'

# definição de EOF
TT_EOF = 'EOF'

DIGITS = '0123456789'
PALAVRAS_RESERVADAS = {
'int': TT_INT,
'double': TT_DOUBLE,
'String': TT_STRING,
'var': TT_VAR,
'if': TT_IF,
'else': TT_ELSE,
'while': TT_WHILE,
'for': TT_FOR,
'return': TT_RETURN,
'print': TT_PRINT
}


class Token:
    def __init__(self, tipo, valor=None, pos_start=None, pos_end=None):
        self.tipo = tipo
        self.valor = valor

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end.copy()

    def __repr__(self):
        if self.valor:
            return f'{self.tipo}:{self.valor}'
        return f'{self.tipo}'

class Lexer:
    def __init__(self,fn, texto):
        self.fn = fn
        self.texto = texto
        self.pos = Position(-1, 0, -1, fn, texto)
        self.current_char = None
        self.advance()  

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.texto[self.pos.idx] if self.pos.idx < len(self.texto) else None

    def make_tokens(self):      
        tokens = []
        while self.current_char != None:
            if self.current_char in '\t\n ':
                self.advance()

            elif self.current_char in DIGITS:
                token, error = self.make_number()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.make_identifier())

            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start = self.pos,))
                self.advance()

            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start = self.pos,))
                self.advance()

            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start = self.pos,))
                self.advance()

            elif self.current_char == '/':
                self.advance()
                if self.current_char == '/':
                    comentario_str = '//'
                    self.advance()
                    while self.current_char != None and self.current_char != '\n':
                        comentario_str += self.current_char
                        self.advance()
                    tokens.append(Token(TT_COMMENT, comentario_str))
                else:
                    tokens.append(Token(TT_DIV, pos_start = self.pos,))

            elif self.current_char == '^':
                tokens.append(Token(TT_POWER, pos_start = self.pos,))
                self.advance()

            elif self.current_char == '<':
                self.advance()

                if self.current_char == '=':
                    tokens.append(Token(TT_LESS_EQ, pos_start = self.pos,))
                    self.advance()
                else:
                    tokens.append(Token(TT_LESS, pos_start = self.pos,))
            elif self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TT_GREATER_EQ, pos_start = self.pos,))
                    self.advance()
                else:
                    tokens.append(Token(TT_GREATER, pos_start = self.pos,))

            elif self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TT_EQ, pos_start = self.pos,))
                    self.advance()
                else:
                    tokens.append(Token(TT_ASSIGN, pos_start = self.pos,))

            elif self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TT_NOT_EQ, pos_start = self.pos,))
                    self.advance()
                else:
                    tokens.append(Token(TT_NOT, pos_start = self.pos,))
            elif self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    tokens.append(Token(TT_AND, pos_start=self.pos))
                    self.advance()
                else:
                    pos_start = self.pos.copy()
                    char = self.current_char
                    self.advance()
                    return [], InvalidCharError(pos_start, self.pos, "'" + char + "'")

            elif self.current_char == '|':
                self.advance()
                if self.current_char == '|':
                    tokens.append(Token(TT_OR, pos_start=self.pos))
                    self.advance()
                else:
                    pos_start = self.pos.copy()
                    char = self.current_char
                    self.advance()
                    return [], InvalidCharError(pos_start, self.pos, "'" + char + "'")

            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start = self.pos,))
                self.advance()

            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start = self.pos,))
                self.advance()

            elif self.current_char == '{':
                tokens.append(Token(TT_LBRACE, pos_start = self.pos,))
                self.advance()

            elif self.current_char == '}':
                tokens.append(Token(TT_RBRACE, pos_start = self.pos,))
                self.advance()

            elif self.current_char == ';':
                tokens.append(Token(TT_SEMI, pos_start = self.pos,))
                self.advance()

            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start = self.pos,))
                self.advance()

            else:
                pos_start = self.pos.copy() 
                char = self.current_char
                self.advance()
                return [], InvalidCharError(pos_start, self.pos,"'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start = self.pos))
        return tokens, None 
            
    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if num_str.endswith('.'):
            return None, InvalidCharError(pos_start, self.pos, "Número real inválido: '" + num_str + "'")
        if dot_count == 0:
            return Token(TT_INTEGER, int(num_str), pos_start, self.pos), None
        else:
            return Token(TT_REAL, float(num_str), pos_start, self.pos), None

    def make_text(self):
        text_str = ''
        pos_start = self.pos.copy()
        self.advance()

        while self.current_char != None and self.current_char != '"':
            text_str += self.current_char
            self.advance()

        if self.current_char == '"':
            self.advance()
            return Token(TT_TEXT, text_str), None
        elif self.current_char == None:
            return None, InvalidCharError(pos_start, self.pos, "String não fechada")

    def make_identifier(self):
        id_str = ''
        while self.current_char != None and (self.current_char.isalpha() or self.current_char.isdigit() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()

        token_type = PALAVRAS_RESERVADAS.get(id_str, TT_IDENTIFIER)
        return Token(token_type, id_str)
########################################
# posicao
########################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt   ):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

########################################
# parte de erros
########################################

class Error:
    def __init__(self,pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end  
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f' File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result
class InvalidCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Invalid Character', details)

class invalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)
        

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
########################################
# parte do parser
########################################
class parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self): 
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok 

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.tipo != TT_EOF:
            return res.failure(invalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Token inesperado"
            ))
        return res

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
        
        elif tok.tipo == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.tipo == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(invalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Esperado ')'"
                ))
        
        return res.failure(invalidSyntaxError(tok.pos_start, tok.pos_end, "Esperado int ou double"))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self): 
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

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
# rodar
########################################   
def run(fn, texto):
    lexer = Lexer(fn, texto)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    p = parser(tokens)
    ast = p.parse()

    return ast.node, ast.error