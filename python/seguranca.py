"""
seguranca.py
Autenticação dos usuários: as senhas nunca são gravadas em texto puro.
Usa-se PBKDF2 (hashlib) com um "sal" aleatório por usuário.
"""

import hashlib
import secrets

MAX_TENTATIVAS = 3
ITERACOES = 100_000

PERFIS = ("administrador", "voluntario", "solicitante")


def gerar_hash(senha, sal=None):
    """Devolve (hash, sal) em hexadecimal."""
    if sal is None:
        sal = secrets.token_hex(16)
    resumo = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"),
                                 bytes.fromhex(sal), ITERACOES)
    return resumo.hex(), sal


def conferir(senha, hash_salvo, sal):
    calculado, _ = gerar_hash(senha, sal)
    return secrets.compare_digest(calculado, hash_salvo)  # comparação segura


def senha_forte(senha):
    """Regra mínima: 6 caracteres, com pelo menos uma letra e um número."""
    return (len(senha) >= 6 and any(c.isdigit() for c in senha)
            and any(c.isalpha() for c in senha))


def criar_usuario(base, nome, login, senha, perfil, pergunta, resposta,
                  pessoa_id=None):
    from dados import proximo_id  # import local evita dependência circular
    if any(u["login"] == login for u in base["usuarios"]):
        raise ValueError("Já existe um usuário com esse login.")
    if perfil not in PERFIS:
        raise ValueError("Perfil inválido.")
    if not senha_forte(senha):
        raise ValueError("A senha deve ter 6+ caracteres, com letras e números.")
    senha_hash, sal = gerar_hash(senha)
    resposta_hash, sal_resposta = gerar_hash(resposta.strip().lower())
    usuario = {
        "id": proximo_id(base, "usuarios"),
        "nome": nome,
        "login": login,
        "senha_hash": senha_hash,
        "sal": sal,
        "perfil": perfil,
        "pergunta": pergunta,
        "resposta_hash": resposta_hash,
        "sal_resposta": sal_resposta,
        "pessoa_id": pessoa_id,
        "tentativas": 0,
        "bloqueado": False,
    }
    base["usuarios"].append(usuario)
    return usuario


def autenticar(base, login, senha):
    """
    Retorna (usuario, mensagem). Após MAX_TENTATIVAS erros seguidos,
    o usuário é bloqueado e só um administrador pode desbloquear.
    """
    usuario = next((u for u in base["usuarios"] if u["login"] == login), None)
    if usuario is None:
        return None, "Login ou senha incorretos."
    if usuario["bloqueado"]:
        return None, "Usuário bloqueado. Procure um administrador."
    if conferir(senha, usuario["senha_hash"], usuario["sal"]):
        usuario["tentativas"] = 0
        return usuario, "Login realizado com sucesso."
    usuario["tentativas"] += 1
    restantes = MAX_TENTATIVAS - usuario["tentativas"]
    if restantes <= 0:
        usuario["bloqueado"] = True
        return None, "Senha incorreta. Usuário bloqueado após 3 tentativas."
    return None, f"Login ou senha incorretos. Tentativas restantes: {restantes}."


def redefinir_senha(base, login, resposta, nova_senha):
    """Recuperação de senha por pergunta de segurança."""
    usuario = next((u for u in base["usuarios"] if u["login"] == login), None)
    if usuario is None:
        return False, "Usuário não encontrado."
    if not conferir(resposta.strip().lower(), usuario["resposta_hash"],
                    usuario["sal_resposta"]):
        return False, "Resposta de segurança incorreta."
    if not senha_forte(nova_senha):
        return False, "A senha deve ter 6+ caracteres, com letras e números."
    usuario["senha_hash"], usuario["sal"] = gerar_hash(nova_senha)
    usuario["tentativas"] = 0
    usuario["bloqueado"] = False
    return True, "Senha redefinida com sucesso."
