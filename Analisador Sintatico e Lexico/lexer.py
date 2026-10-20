from erros import *
########################################
# tokens
########################################
TT_INT, TT_DOUBLE, TT_STRING = 'INT', 'DOUBLE', 'STRING'
TT_MAIN, TT_IF, TT_ELSE, TT_WHILE, TT_PRINT = 'MAIN', 'IF', 'ELSE', 'WHILE', 'PRINT'

# operadores matematicos
TT_PLUS, TT_MINUS, TT_MUL, TT_DIV = 'PLUS', 'MINUS', 'MUL', 'DIV' # + - * /

# operadores logicos e atribuicao
TT_LESS, TT_GREATER, TT_LESS_EQ, TT_GREATER_EQ = 'LESS', 'GREATER', 'LESS_EQ', 'GREATER_EQ' # < > <= >=
TT_EQ, TT_NOT_EQ, TT_AND, TT_OR, TT_ASSIGN = 'EQ', 'NOT_EQ', 'AND', 'OR', 'ASSIGN' # == != && || =

# separadores
TT_LPAREN, TT_RPAREN, TT_LBRACE, TT_RBRACE = 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE' # ( ) { }
TT_SEMI, TT_COMMA = 'SEMI', 'COMMA' # ; ,

# comentario, variaveis, numeros, texto e fim do arquivo
TT_COMMENT = 'COMMENT' # //
TT_IDENTIFIER, TT_REAL, TT_INTEGER, TT_TEXT = 'IDENTIFIER', 'REAL', 'INTEGER', 'TEXT'
TT_EOF = 'EOF'

DIGITS = '0123456789'
PALAVRAS_RESERVADAS = {
'int': TT_INT,
'double': TT_DOUBLE,
'String': TT_STRING,
'main': TT_MAIN,
'if': TT_IF,
'else': TT_ELSE,
'while': TT_WHILE,
'print': TT_PRINT
}
TIPOS_DADO = (TT_INT, TT_DOUBLE, TT_STRING)

# tokens de 1 caractere e de 1 ou 2 caracteres (ex: < e <=)
SIMPLES = {'+': TT_PLUS, '-': TT_MINUS, '*': TT_MUL, '(': TT_LPAREN, ')': TT_RPAREN,
           '{': TT_LBRACE, '}': TT_RBRACE, ';': TT_SEMI, ',': TT_COMMA}
DUPLOS = {'<': (TT_LESS, TT_LESS_EQ), '>': (TT_GREATER, TT_GREATER_EQ), '=': (TT_ASSIGN, TT_EQ)}


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

    # linha do token no arquivo (usada nas tabelas)
    @property
    def linha(self):
        return self.pos_start.ln + 1

    # texto original do token (usado nas mensagens de erro)
    @property
    def lexema(self):
        if self.tipo == TT_EOF:
            return 'fim do arquivo'
        return self.pos_start.ftxt[self.pos_start.idx:self.pos_end.idx]

    def __repr__(self):
        if self.valor is not None:
            return f'{self.tipo}:{self.valor}'
        return f'{self.tipo}'

class Lexer:
    def __init__(self, fn, texto):
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
            c = self.current_char
            if c in '\t\r\n ':
                self.advance()

            elif c in DIGITS or c.isalpha() or c == '_' or c in '"\'':
                if c in DIGITS: token, error = self.make_number()
                elif c in '"\'': token, error = self.make_text()
                else: token, error = self.make_identifier()
                if error:
                    return [], error
                tokens.append(token)

            elif c in SIMPLES:
                tokens.append(Token(SIMPLES[c], pos_start = self.pos))
                self.advance()

            elif c == '/':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '/':
                    comentario_str = '//'
                    self.advance()
                    while self.current_char != None and self.current_char != '\n':
                        comentario_str += self.current_char
                        self.advance()
                    tokens.append(Token(TT_COMMENT, comentario_str, pos_start, self.pos))
                else:
                    tokens.append(Token(TT_DIV, pos_start = pos_start, pos_end = self.pos))

            elif c in DUPLOS:
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(DUPLOS[c][1], pos_start = pos_start, pos_end = self.pos))
                else:
                    tokens.append(Token(DUPLOS[c][0], pos_start = pos_start, pos_end = self.pos))

            elif c == '!':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    tokens.append(Token(TT_NOT_EQ, pos_start = pos_start, pos_end = self.pos))
                else:
                    return [], InvalidCharError(pos_start, self.pos, "'!' isolado (use '!=')")

            elif c in '&|':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == c:
                    self.advance()
                    tokens.append(Token(TT_AND if c == '&' else TT_OR, pos_start = pos_start, pos_end = self.pos))
                else:
                    return [], InvalidCharError(pos_start, self.pos, "'" + c + "' isolado (use '" + c + c + "')")

            else:
                pos_start = self.pos.copy() 
                self.advance()
                return [], InvalidCharError(pos_start, self.pos, "'" + c + "'")

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
        if self.current_char != None and (self.current_char.isalpha() or self.current_char == '_'):
            return None, InvalidCharError(pos_start, self.pos, "Identificador não pode começar com número: '" + num_str + self.current_char + "...'")
        if dot_count == 0:
            return Token(TT_INTEGER, int(num_str), pos_start, self.pos), None
        else:
            return Token(TT_REAL, float(num_str), pos_start, self.pos), None

    def make_text(self):
        text_str = ''
        pos_start = self.pos.copy()
        aspas = self.current_char
        self.advance()

        while self.current_char != None and self.current_char != aspas and self.current_char != '\n':
            text_str += self.current_char
            self.advance()

        if self.current_char == aspas:
            self.advance()
            return Token(TT_TEXT, text_str, pos_start, self.pos), None
        return None, InvalidCharError(pos_start, self.pos, "String não fechada")

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()
        while self.current_char != None and (self.current_char.isalpha() or self.current_char.isdigit() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()

        if not id_str[0].isalpha():
            return None, InvalidCharError(pos_start, self.pos, "Identificador '" + id_str + "' deve começar com letra")
        if id_str.endswith('_'):
            return None, InvalidCharError(pos_start, self.pos, "Identificador '" + id_str + "' não pode terminar em '_'")

        token_type = PALAVRAS_RESERVADAS.get(id_str, TT_IDENTIFIER)
        return Token(token_type, id_str, pos_start, self.pos), None
