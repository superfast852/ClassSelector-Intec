from pickle import load
# This program works after we generate the csv files with the data from the presec_analyzer.

with open("codigos.txt", "r") as f:
    codigos = [code for code in f.read().split("\n") if code]

for codigo in codigos:
    print(f"Codigo: {codigo}")
    with open(f"materias/{codigo}.pkl", "rb") as f:
        secciones = load(f)
    for materia in secciones:
        print(materia)
    print()
