import reconhecedor

nome = input('Arquivo do programa> ')
with open(nome, encoding='utf-8') as f:
    texto = f.read()

tokens, ast, simbolos, codigos, error = reconhecedor.compilar(nome, texto)

if error: print(error.as_string())
else:
    print(reconhecedor.tabela_simbolos(simbolos))
    print()
    print(reconhecedor.tabela_codigos(codigos))