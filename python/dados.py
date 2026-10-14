"""
dados.py
Camada de persistência: carrega e grava a base em arquivo JSON e realiza
o backup automático a cada gravação (mantendo as cópias mais recentes).
"""

import json
import os
import shutil
from datetime import datetime

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")
ARQUIVO_BASE = os.path.join(PASTA_DADOS, "base.json")
PASTA_BACKUP = os.path.join(PASTA_DADOS, "backup")
MAX_BACKUPS = 5

COLECOES = ["usuarios", "pessoas", "produtos", "movimentacoes", "solicitacoes"]


def base_vazia():
    return {colecao: [] for colecao in COLECOES}


def carregar():
    """Lê a base do disco. Se o arquivo não existir ou estiver corrompido,
    tenta recuperar pelo backup mais recente."""
    os.makedirs(PASTA_DADOS, exist_ok=True)
    if not os.path.exists(ARQUIVO_BASE):
        return base_vazia()
    try:
        with open(ARQUIVO_BASE, "r", encoding="utf-8") as arquivo:
            base = json.load(arquivo)
    except (json.JSONDecodeError, OSError):
        base = _recuperar_backup()
    for colecao in COLECOES:  # garante que todas as coleções existem
        base.setdefault(colecao, [])
    return base


def salvar(base):
    """Grava a base de forma segura (arquivo temporário + troca) e faz backup."""
    os.makedirs(PASTA_DADOS, exist_ok=True)
    temporario = ARQUIVO_BASE + ".tmp"
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(base, arquivo, ensure_ascii=False, indent=2)
    os.replace(temporario, ARQUIVO_BASE)  # troca atômica: evita arquivo pela metade
    fazer_backup()


def fazer_backup():
    os.makedirs(PASTA_BACKUP, exist_ok=True)
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    shutil.copy2(ARQUIVO_BASE, os.path.join(PASTA_BACKUP, f"base_{carimbo}.json"))
    backups = sorted(os.listdir(PASTA_BACKUP))
    while len(backups) > MAX_BACKUPS:  # rotação: remove os mais antigos
        os.remove(os.path.join(PASTA_BACKUP, backups.pop(0)))


def listar_backups():
    if not os.path.isdir(PASTA_BACKUP):
        return []
    return sorted(os.listdir(PASTA_BACKUP), reverse=True)


def restaurar_backup(nome_arquivo):
    origem = os.path.join(PASTA_BACKUP, nome_arquivo)
    shutil.copy2(origem, ARQUIVO_BASE)


def _recuperar_backup():
    for nome in listar_backups():
        try:
            with open(os.path.join(PASTA_BACKUP, nome), encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except (json.JSONDecodeError, OSError):
            continue
    return base_vazia()


def proximo_id(base, colecao):
    """Gera o próximo código sequencial da coleção."""
    registros = base[colecao]
    return max((r["id"] for r in registros), default=0) + 1


def agora_iso():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
