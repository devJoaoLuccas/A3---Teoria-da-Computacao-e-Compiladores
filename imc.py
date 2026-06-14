# Código gerado automaticamente pelo Transpilador Latim -> Python
nome = ""
piso = 0.0
statura = 0.0
imc = 0.0
continuar = 0
continuar = 1
while continuar == 1:
    print("Insira o nome do paciente:")
    nome = input()
    print("Insira o peso (em kg, ex: 70.5):")
    piso = float(input())
    print("Insira a altura (em metros, ex: 1.75):")
    statura = float(input())
    imc = piso / (statura * statura)
    print("O IMC calculado para o paciente é:")
    print(imc)
    if imc < 18.5:
        print("Classificação: Abaixo do peso.")
    else:
        if imc < 25.0:
            print("Classificação: Peso normal.")
        else:
            if imc < 30.0:
                print("Classificação: Sobrepeso.")
            else:
                print("Classificação: Obesidade.")
    print("Deseja calcular o IMC de outro paciente? (1 para Sim, 0 para Não):")
    continuar = int(input())
