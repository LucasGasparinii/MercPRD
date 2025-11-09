import sqlite3
import datetime
import os

def criar_banco_de_dados():
    """
    Cria ou se conecta ao banco de dados e cria a tabela 'usuarios'.
    Adiciona a coluna 'is_admin' se ela não existir.
    """
    try:
        conn = sqlite3.connect('mercprd.db')
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        """)

        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = [info[1] for info in cursor.fetchall()]
        if 'is_admin' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN is_admin INTEGER DEFAULT 0;")
        
        conn.commit()
        print("Banco de dados 'mercprd.db' e a tabela 'usuarios' prontos.")

    except sqlite3.Error as e:
        print(f"Erro ao criar o banco de dados: {e}")

    finally:
        if conn:
            conn.close()

def saudacao():
    """Retorna uma saudação de 'Bom dia', 'Boa tarde' ou 'Boa noite'."""
    agora = datetime.datetime.now()
    hora = agora.hour

    if 6 <= hora < 12:
        return "Bom dia!"
    elif 12 <= hora < 18:
        return "Boa tarde!"
    else:
        return "Boa noite!"

def registrar_usuario():
    """
    Permite ao usuário criar uma nova conta (não-admin) e armazena no banco de dados.
    """
    print("\n--- Criação de nova conta ---")
    username = input("Digite um nome de usuário: ")
    password = input("Digite uma senha: ")

    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
        print("\nErro: A senha deve ter no mínimo 8 caracteres, com pelo menos uma letra e um número.")
        return

    username_lower = username.lower()

    try:
        conn = sqlite3.connect('mercprd.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO usuarios (username, password, is_admin) VALUES (?, ?, ?)", (username_lower, password, 0))
        
        conn.commit()
        print("\nConta criada com sucesso! Agora você pode fazer o login.")

    except sqlite3.IntegrityError:
        print("\nErro: Este nome de usuário já existe. Por favor, escolha outro.")

    except sqlite3.Error as e:
        print(f"\nErro ao registrar usuário: {e}")

    finally:
        if conn:
            conn.close()

def fazer_login():
    """
    Permite ao usuário fazer login e verifica se é um administrador.
    """
    print("\n--- Acesso à conta ---")
    username = input("Usuário: ")
    password = input("Senha: ")

    username_lower = username.lower()

    try:
        conn = sqlite3.connect('mercprd.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username_lower, password))
        usuario = cursor.fetchone()

        if usuario:
            print(f"\nLogin bem-sucedido! Bem-vindo(a), {usuario[0].capitalize()}!")
            is_admin = usuario[2]
            if is_admin == 1:
                menu_admin()
            else:
                menu_usuario()
        else:
            print("\nErro: Usuário ou senha inválidos. Tente novamente.")

    except sqlite3.Error as e:
        print(f"\nErro ao fazer login: {e}")

    finally:
        if conn:
            conn.close()

def trocar_senha():
    """
    Permite ao usuário trocar a senha da sua conta após validar o usuário e a senha atual.
    """
    print("\n--- Troca de Senha ---")
    username = input("Digite seu nome de usuário: ")
    senha_atual = input("Digite sua senha atual: ")

    username_lower = username.lower()

    try:
        conn = sqlite3.connect('mercprd.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username_lower, senha_atual))
        usuario = cursor.fetchone()

        if not usuario:
            print("\nErro: Usuário ou senha atual inválidos.")
            return

        nova_senha = input("Digite sua nova senha: ")

        if len(nova_senha) < 8 or not any(char.isdigit() for char in nova_senha) or not any(char.isalpha() for char in nova_senha):
            print("\nErro: A nova senha deve ter no mínimo 8 caracteres, com pelo menos uma letra e um número.")
            return

        cursor.execute("UPDATE usuarios SET password = ? WHERE username = ?", (nova_senha, username_lower))
        conn.commit()
        print("\nSenha alterada com sucesso!")

    except sqlite3.Error as e:
        print(f"\nErro ao trocar a senha: {e}")

    finally:
        if conn:
            conn.close()

# --- Funções exclusivas do Administrador ---

def criar_admin():
    """Cria a primeira conta de administrador."""
    print("\n--- Criação da Conta de Administrador ---")
    print("Esta operação deve ser feita apenas uma vez.")
    username = input("Digite o nome de usuário do administrador: ")
    password = input("Digite a senha do administrador: ")

    username_lower = username.lower()

    try:
        conn = sqlite3.connect('mercprd.db')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE is_admin = 1")
        if cursor.fetchone()[0] > 0:
            print("\nErro: Já existe uma conta de administrador. Não é possível criar outra.")
            return
        
        cursor.execute("INSERT INTO usuarios (username, password, is_admin) VALUES (?, ?, ?)", (username_lower, password, 1))
        
        conn.commit()
        print("\nConta de administrador criada com sucesso!")

    except sqlite3.IntegrityError:
        print("\nErro: Este nome de usuário já existe.")

    finally:
        if conn:
            conn.close()

def excluir_conta(username_to_delete=None):
    """Permite ao administrador excluir uma conta de usuário."""
    if username_to_delete is None:
        print("\n--- Excluir Conta de Usuário ---")
        username = input("Digite o nome de usuário da conta que deseja excluir: ")
    else:
        username = username_to_delete

    username_lower = username.lower()

    try:
        conn = sqlite3.connect('mercprd.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username_lower,))
        usuario = cursor.fetchone()

        if not usuario:
            print(f"\nErro: Usuário '{username}' não encontrado.")
            return

        confirmacao = input(f"Tem certeza que deseja excluir a conta de '{username}'? (s/n): ")
        if confirmacao.lower() != 's':
            print("\nOperação cancelada.")
            return

        cursor.execute("DELETE FROM usuarios WHERE username = ?", (username_lower,))
        conn.commit()
        print(f"\nConta de '{username}' excluída com sucesso.")

    except sqlite3.Error as e:
        print(f"Erro ao excluir a conta: {e}")

    finally:
        if conn:
            conn.close()

def alterar_senha_admin(username_to_alter=None):
    """Permite ao administrador alterar a senha de qualquer conta."""
    if username_to_alter is None:
        print("\n--- Alterar Senha de Usuário ---")
        username = input("Digite o nome de usuário da conta a ser alterada: ")
    else:
        username = username_to_alter

    username_lower = username.lower()

    try:
        conn = sqlite3.connect('mercprd.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username_lower,))
        usuario = cursor.fetchone()

        if not usuario:
            print("\nErro: Usuário não encontrado.")
            return

        nova_senha = input("Digite a nova senha para esta conta: ")

        if len(nova_senha) < 8 or not any(char.isdigit() for char in nova_senha) or not any(char.isalpha() for char in nova_senha):
            print("\nErro: A nova senha deve ter no mínimo 8 caracteres, com pelo menos uma letra e um número.")
            return

        cursor.execute("UPDATE usuarios SET password = ? WHERE username = ?", (nova_senha, username_lower))
        conn.commit()
        print(f"\nSenha do usuário '{username}' alterada com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro ao alterar a senha: {e}")

    finally:
        if conn:
            conn.close()

def visualizar_contas_e_gerenciar():
    """
    Permite ao administrador visualizar todas as contas cadastradas e
    oferece a opção de gerenciar (excluir ou alterar senha).
    """
    print("\n--- Gerenciamento de Contas ---")
    try:
        conn = sqlite3.connect('mercprd.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, is_admin FROM usuarios ORDER BY username")
        usuarios = cursor.fetchall()
        
        if not usuarios:
            print("Nenhum usuário cadastrado.")
            return

        for usuario in usuarios:
            status = "Administrador" if usuario[1] == 1 else "Usuário Comum"
            print(f" - Usuário: {usuario[0].capitalize()} ({status})")

        print("-" * 30)
        
        while True:
            opcao = input("Deseja alterar ou excluir alguma conta? (s/n): ")
            if opcao.lower() == 's':
                acao = input("Digite 'a' para Alterar senha ou 'e' para Excluir conta: ")
                if acao.lower() == 'a':
                    alterar_senha_admin()
                elif acao.lower() == 'e':
                    excluir_conta()
                else:
                    print("Opção inválida.")
                
                print("\nLista de contas atualizada:")
                cursor.execute("SELECT username, is_admin FROM usuarios ORDER BY username")
                usuarios = cursor.fetchall()
                for usuario in usuarios:
                    status = "Administrador" if usuario[1] == 1 else "Usuário Comum"
                    print(f" - Usuário: {usuario[0].capitalize()} ({status})")
                print("-" * 30)

            elif opcao.lower() == 'n':
                print("Voltando ao menu principal do administrador.")
                break
            else:
                print("Opção inválida. Por favor, digite 's' ou 'n'.")

    except sqlite3.Error as e:
        print(f"Erro ao visualizar contas: {e}")

    finally:
        if conn:
            conn.close()

def menu_admin():
    """Menu exclusivo para administradores."""
    while True:
        print("\n--- Menu do Administrador ---")
        print("1 - Visualizar e Gerenciar Contas")
        print("2 - Trocar minha senha")
        print("3 - Sair do menu de administrador")
        
        opcao = input("Escolha uma opção (1, 2 ou 3): ")

        if opcao == '1':
            visualizar_contas_e_gerenciar()
        elif opcao == '2':
            trocar_senha()
        elif opcao == '3':
            print("\nSaindo do menu de administrador...")
            break
        else:
            print("\nOpção inválida. Por favor, tente novamente.")

def menu_usuario():
    """Menu para usuários comuns."""
    while True:
        print("\n--- Menu do Usuário Comum ---")
        print("1 - Trocar minha senha")
        print("2 - Sair")

        opcao = input("Escolha uma opção (1 ou 2): ")
        if opcao == '1':
            trocar_senha()
        elif opcao == '2':
            print("\nSaindo do menu de usuário...")
            break
        else:
            print("\nOpção inválida. Por favor, tente novamente.")

def main():
    """Função principal que gerencia o fluxo do programa."""
    criar_banco_de_dados()

    print(f"\n{saudacao()} Bem-vindo(a) ao Sistema MercPrd.")

    while True:
        print("\nPor favor, selecione uma das opções abaixo para continuar:")
        print("1 - Fazer login")
        print("2 - Criar uma nova conta")
        print("3 - Trocar senha (para quem esqueceu)")
        print("4 - Sair")
        
        conn = sqlite3.connect('mercprd.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE is_admin = 1")
        if cursor.fetchone()[0] == 0:
            print("--- ATENÇÃO: Nenhum administrador cadastrado. ---")
            print("Para criar o administrador, digite 'admin'")
        conn.close()

        opcao = input("Escolha uma opção (1, 2, 3, 4 ou 'admin'): ")

        if opcao == '1':
            fazer_login()
        elif opcao == '2':
            registrar_usuario()
        elif opcao == '3':
            trocar_senha()
        elif opcao == '4':
            print("\nObrigado por usar o sistema. Até mais!")
            break
        elif opcao.lower() == 'admin':
            criar_admin()
        else:
            print("\nOpção inválida. Por favor, tente novamente.")

if __name__ == "__main__":
    main()