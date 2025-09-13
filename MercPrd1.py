import datetime
#Criando o inicio dp programa com a Opção de Cadastro
def saudacao():
    """Retorna uma saudação de 'Bom dia', 'Boa tarde' ou 'Boa noite'."""
    # Pega o horário atual
    agora = datetime.datetime.now()
    hora = agora.hour

    if 6 <= hora < 12:
        return "Bom dia!"
    elif 12 <= hora < 18:
        return "Boa tarde!"
    else:
        return "Boa noite!"

def main():
    """Função principal que executa a saudação e as mensagens do sistema."""
    # Exibe a saudação de acordo com o horário
    print(f"{saudacao()}Bem Vindo(a) ao Sistema MercPrd.\n")

    # Exibe as opções de login ou criação de conta
    print("Por favor, selecione uma das opções abaixo para continuar:")
    print("1 - Fazer login")
    print("2 - Criar uma nova conta")

if __name__ == "__main__":
    main()