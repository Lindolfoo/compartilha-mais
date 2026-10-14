"""
interface.py
Funções de apoio à interface em modo texto: limpeza de tela, cabeçalhos,
leitura validada de dados e tabelas que se ajustam à largura do terminal.
"""

import os
import shutil
import sys
from datetime import date, datetime

FORMATO_DATA = "%d/%m/%Y"


# ----------------------------------------------------------------------
# TELA
# ----------------------------------------------------------------------
def limpar_tela():
    """Limpa o terminal no Windows (cls) ou Linux/macOS (clear)."""
    if sys.stdout.isatty():  # só limpa quando há um terminal de verdade
        os.system("cls" if os.name == "nt" else "clear")


def largura_tela():
    """Largura atual do terminal, limitada entre 60 e 100 colunas."""
    colunas = shutil.get_terminal_size((80, 24)).columns
    return max(60, min(colunas, 100))


def cabecalho(titulo, usuario=None):
    limpar_tela()
    largura = largura_tela()
    print("=" * largura)
    print("COMPARTILHA+ | Gestão de Produtos Colaborativos".center(largura))
    print("=" * largura)
    if usuario:
        info = f"Usuário: {usuario['nome']} ({usuario['perfil']})"
        print(info + date.today().strftime(FORMATO_DATA).rjust(largura - len(info)))
        print("-" * largura)
    print(f">> {titulo.upper()}\n")


def pausar():
    input("\nPressione ENTER para continuar...")


def mensagem(texto, tipo="info"):
    prefixos = {"info": "[i]", "ok": "[OK]", "erro": "[ERRO]", "alerta": "[!]"}
    print(f"{prefixos.get(tipo, '')} {texto}")


def menu(opcoes):
    """Exibe as opções numeradas e devolve a escolhida (texto)."""
    for chave, descricao in opcoes:
        print(f"  {chave} - {descricao}")
    return input("\nEscolha uma opção: ").strip()


# ----------------------------------------------------------------------
# LEITURA VALIDADA
# ----------------------------------------------------------------------
def ler_texto(rotulo, obrigatorio=True, minimo=1):
    while True:
        valor = input(f"{rotulo}: ").strip()
        if not obrigatorio and valor == "":
            return ""
        if len(valor) >= minimo:
            return valor
        mensagem(f"Campo obrigatório (mínimo de {minimo} caractere(s)).", "erro")


def ler_inteiro(rotulo, minimo=None, maximo=None, permitir_vazio=False):
    while True:
        valor = input(f"{rotulo}: ").strip()
        if permitir_vazio and valor == "":
            return None
        try:
            numero = int(valor)
        except ValueError:
            mensagem("Digite um número inteiro válido.", "erro")
            continue
        if minimo is not None and numero < minimo:
            mensagem(f"O valor deve ser maior ou igual a {minimo}.", "erro")
        elif maximo is not None and numero > maximo:
            mensagem(f"O valor deve ser menor ou igual a {maximo}.", "erro")
        else:
            return numero


def ler_decimal(rotulo, minimo=0.0):
    while True:
        valor = input(f"{rotulo}: ").strip().replace(",", ".")
        try:
            numero = float(valor)
            if numero < minimo:
                raise ValueError
            return round(numero, 3)
        except ValueError:
            mensagem(f"Digite um número válido (mínimo {minimo}).", "erro")


def ler_data(rotulo, permitir_vazio=False, permitir_passado=True):
    """Lê uma data no formato DD/MM/AAAA usando a biblioteca datetime."""
    while True:
        valor = input(f"{rotulo} (DD/MM/AAAA): ").strip()
        if permitir_vazio and valor == "":
            return None
        try:
            data_lida = datetime.strptime(valor, FORMATO_DATA).date()
        except ValueError:
            mensagem("Data inválida. Use o formato DD/MM/AAAA.", "erro")
            continue
        if not permitir_passado and data_lida < date.today():
            mensagem("A data não pode estar no passado.", "erro")
            continue
        return data_lida


def percentual(valor):
    """Formata um percentual no padrão brasileiro: 59.04 -> '59,0%'."""
    return f"{valor:.1f}%".replace(".", ",")


def confirmar(pergunta):
    return input(f"{pergunta} (S/N): ").strip().upper() == "S"


# ----------------------------------------------------------------------
# DATAS
# ----------------------------------------------------------------------
def para_texto(data_iso):
    """'2026-10-12' -> '12/10/2026' (aceita None)."""
    if not data_iso:
        return "-"
    return datetime.strptime(data_iso[:10], "%Y-%m-%d").strftime(FORMATO_DATA)


def para_data(data_iso):
    return datetime.strptime(data_iso[:10], "%Y-%m-%d").date()


def dias_ate(data_iso):
    """Quantidade de dias entre hoje e a data (negativo = já passou)."""
    return (para_data(data_iso) - date.today()).days


# ----------------------------------------------------------------------
# TABELA
# ----------------------------------------------------------------------
def tabela(colunas, linhas):
    """
    Imprime uma tabela. 'colunas' é uma lista de (titulo, largura).
    Se o terminal for estreito, a última coluna é reduzida.
    """
    if not linhas:
        mensagem("Nenhum registro encontrado.")
        return
    larguras = [l for _, l in colunas]
    excesso = sum(larguras) + len(larguras) - largura_tela()
    if excesso > 0:
        larguras[-1] = max(8, larguras[-1] - excesso)
    titulo = " ".join(t[:l].ljust(l) for (t, _), l in zip(colunas, larguras))
    print(titulo)
    print("-" * len(titulo))
    for linha in linhas:
        print(" ".join(str(v)[:l].ljust(l) for v, l in zip(linha, larguras)))
    print(f"\nTotal de registros: {len(linhas)}")
