# Definição palavras reservadas
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
    def __init__(self, tipo, valor=None):
        self.tipo = tipo
        self.valor = valor

    def __repr__(self):
        if self.valor:
            return f'{self.tipo}:{self.valor}'
        return f'{self.tipo}'

class Lexer:
    def __init__(self, texto):
        self.texto = texto
        self.pos = -1
        self.current_char = None
        self.advance()  

    def advance(self):
        self.pos += 1
        if self.pos < len(self.texto):
            self.current_char = self.texto[self.pos]
        else:
            self.current_char = None

    def make_tokens(self):      
        tokens = []
        while self.current_char != None:
            if self.current_char in '\t\n ':
                self.advance()

            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '"':
                token, error = self.make_text()
                if error:
                    return [], error
                tokens.append(token)

            elif self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.make_identifier())

            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, '+'))
                self.advance()

            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, '-'))
                self.advance()

            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, '*'))
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
                    tokens.append(Token(TT_DIV, '/'))

            elif self.current_char == '^':
                tokens.append(Token(TT_POWER, '^'))
                self.advance()

            elif self.current_char == '<':
                self.advance()

                if self.current_char == '=':
                    tokens.append(Token(TT_LESS_EQ, '<='))
                    self.advance()
                else:
                    tokens.append(Token(TT_LESS, '<'))
            elif self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TT_GREATER_EQ, '>='))
                    self.advance()
                else:
                    tokens.append(Token(TT_GREATER, '>'))

            elif self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TT_EQ, '=='))
                    self.advance()
                else:
                    tokens.append(Token(TT_ASSIGN, '='))

            elif self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TT_NOT_EQ, '!='))
                    self.advance()
                else:
                    tokens.append(Token(TT_NOT, '!'))

            elif self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    tokens.append(Token(TT_AND, '&&'))
                    self.advance()
                else:
                    char = self.current_char
                    self.advance()
                    return [], InvalidCharError("'" + char + "'")

            elif self.current_char == '|':
                self.advance()
                if self.current_char == '|':
                    tokens.append(Token(TT_OR, '||'))
                    self.advance()
                else:
                    char = self.current_char
                    self.advance()
                    return [], InvalidCharError("'" + char + "'")

            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, '('))
                self.advance()

            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, ')'))
                self.advance()

            elif self.current_char == '{':
                tokens.append(Token(TT_LBRACE, '{'))
                self.advance()

            elif self.current_char == '}':
                tokens.append(Token(TT_RBRACE, '}'))
                self.advance()

            elif self.current_char == ';':
                tokens.append(Token(TT_SEMI, ';'))
                self.advance()

            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, ','))
                self.advance()

            else:
                char = self.current_char
                self.advance()
                return [], InvalidCharError("'" + char + "'")

        tokens.append(Token(TT_EOF))
        return tokens, None 
            
    def make_number(self):
        num_str = ''
        dot_count = 0
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        
        if dot_count == 0:
            return Token(TT_INTEGER, int(num_str))
        else:
            return Token(TT_REAL, float(num_str))

    def make_text(self):
        text_str = ''

        self.advance()

        while self.current_char != None and self.current_char != '"':
            text_str += self.current_char
            self.advance()

        if self.current_char == '"':
            self.advance()
            return Token(TT_TEXT, text_str), None
        elif self.current_char == None:    
            return None, InvalidCharError("String não fechada")

    def make_identifier(self):
        id_str = ''
        while self.current_char != None and (self.current_char.isalpha() or self.current_char.isdigit() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()

        token_type = PALAVRAS_RESERVADAS.get(id_str, TT_IDENTIFIER)
        return Token(token_type, id_str)
    
class Error:
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        return result
class InvalidCharError(Error):
    def __init__(self, details):
        super().__init__('Invalid Character', details)
            
def run(texto):
    lexer = Lexer(texto)
    tokens, error = lexer.make_tokens()
    return tokens, error