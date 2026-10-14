"""
main.py
Ponto de entrada do sistema Compartilha+ – Gestão de Produtos Colaborativos.

Uso:
    python main.py          inicia o sistema
    python main.py --demo   recria a base com dados de demonstração
"""

import sys

import dados
import seguranca
from interface import cabecalho, mensagem, ler_texto, pausar
from telas import tela_login, menu_principal, seguranca_ler_senha


def primeiro_acesso(base):
    """Na primeira execução não há usuários: cadastra o administrador."""
    cabecalho("Primeiro acesso – cadastro do administrador")
    print("Nenhum usuário encontrado. Cadastre o administrador do sistema.\n")
    while True:
        nome = ler_texto("Nome completo", minimo=3)
        login = ler_texto("Login", minimo=3)
        senha = seguranca_ler_senha("Senha (6+ caracteres, letras e números)")
        pergunta = ler_texto("Pergunta de segurança")
        resposta = ler_texto("Resposta")
        try:
            seguranca.criar_usuario(base, nome, login, senha, "administrador",
                                    pergunta, resposta)
            dados.salvar(base)
            mensagem("Administrador cadastrado.", "ok")
            pausar()
            return
        except ValueError as erro:
            mensagem(str(erro), "erro")


def main():
    if "--demo" in sys.argv:
        from demo import criar_base_demo
        dados.salvar(criar_base_demo())
        print("Base de demonstração criada (login: admin / senha: admin123).")

    base = dados.carregar()
    if not base["usuarios"]:
        primeiro_acesso(base)

    while True:
        usuario = tela_login(base)
        if usuario is None:
            print("\nSistema encerrado. Até logo!")
            break
        menu_principal(base, usuario)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nSistema encerrado pelo usuário.")
