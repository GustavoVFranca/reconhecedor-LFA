import reconhecedor

while True:
    text = input('LFA> ')
    lexer = reconhecedor.Lexer('<stdin>', text)
    tokens, error = lexer.make_tokens()

    if error: print(error.as_string())
    else: print(tokens)