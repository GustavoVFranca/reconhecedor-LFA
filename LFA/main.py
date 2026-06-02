import reconhecedor

while True:
    text = input('LFA> ')
    result, error = reconhecedor.run(text)

    if error: print(error.as_string())
    else: print(result)