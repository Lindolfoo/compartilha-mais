"""
servicos.py
Regras de negócio do sistema. Este módulo não lê teclado nem imprime na
tela: recebe dados e devolve resultados, o que permite testá-lo de forma
automatizada (ver a pasta testes/).
"""

from datetime import date, timedelta

from dados import proximo_id, agora_iso
from estruturas import ArvoreBST, Fila, merge_sort, busca_binaria
from interface import dias_ate

CATEGORIAS = ["Alimentos", "Higiene", "Medicamentos", "Brinquedos",
              "Vestuário", "Outros"]
EXIGEM_VALIDADE = {"Alimentos", "Higiene", "Medicamentos"}
DIAS_ALERTA = 30  # produtos que vencem em até 30 dias geram alerta


class RegraNegocioErro(Exception):
    """Erro de validação de regra de negócio (mensagem amigável ao usuário)."""


# ----------------------------------------------------------------------
# CONSULTAS GERAIS
# ----------------------------------------------------------------------
def por_id(base, colecao, codigo):
    """Busca binária pelo id (as coleções são mantidas em ordem crescente)."""
    return busca_binaria(base[colecao], codigo, chave=lambda r: r["id"])


def indice_produtos(base):
    """Monta a árvore binária de busca com os nomes dos produtos."""
    arvore = ArvoreBST()
    for produto in base["produtos"]:
        arvore.inserir(produto["nome"], produto["id"])
    return arvore


def lote_valido(produto):
    """Um lote está disponível se tem saldo e não está vencido."""
    if produto["quantidade"] <= 0 or produto.get("descartado"):
        return False
    return produto["validade"] is None or dias_ate(produto["validade"]) >= 0


def catalogo_disponivel(base):
    """Agrupa os lotes válidos por nome: {nome: quantidade total}."""
    catalogo = {}
    arvore = indice_produtos(base)
    for pid in arvore.em_ordem():  # já sai em ordem alfabética
        produto = por_id(base, "produtos", pid)
        if lote_valido(produto):
            catalogo[produto["nome"]] = catalogo.get(produto["nome"], 0) \
                + produto["quantidade"]
    return catalogo


def filtrar_produtos(base, prefixo="", categoria=None, vence_em=None,
                     somente_disponiveis=True):
    """Filtros combináveis: prefixo do nome, categoria e prazo de validade."""
    arvore = indice_produtos(base)
    ids = arvore.buscar_prefixo(prefixo) if prefixo else arvore.em_ordem()
    resultado = []
    for pid in ids:
        produto = por_id(base, "produtos", pid)
        if somente_disponiveis and not lote_valido(produto):
            continue
        if categoria and produto["categoria"] != categoria:
            continue
        if vence_em is not None:
            if produto["validade"] is None or dias_ate(produto["validade"]) > vence_em:
                continue
        resultado.append(produto)
    return resultado


# ----------------------------------------------------------------------
# CADASTROS
# ----------------------------------------------------------------------
def cadastrar_pessoa(base, nome, documento, telefone, email, tipo):
    if tipo not in ("doador", "solicitante"):
        raise RegraNegocioErro("Tipo de pessoa inválido.")
    documento = "".join(c for c in documento if c.isdigit())
    if len(documento) not in (11, 14):
        raise RegraNegocioErro("Informe um CPF (11 dígitos) ou CNPJ (14 dígitos).")
    if any(p["documento"] == documento and p["tipo"] == tipo
           for p in base["pessoas"]):
        raise RegraNegocioErro(f"Já existe um {tipo} com esse documento.")
    pessoa = {
        "id": proximo_id(base, "pessoas"),
        "nome": nome.strip(),
        "documento": documento,
        "telefone": telefone,
        "email": email,
        "tipo": tipo,
        "cadastro": agora_iso(),
    }
    base["pessoas"].append(pessoa)
    return pessoa


def pessoas_do_tipo(base, tipo):
    return [p for p in base["pessoas"] if p["tipo"] == tipo]


# ----------------------------------------------------------------------
# DOAÇÃO (ENTRADA NO ESTOQUE)
# ----------------------------------------------------------------------
def padronizar_nome(nome):
    """Remove espaços extras e deixa a primeira letra maiúscula, para que
    'arroz 5kg' e 'Arroz  5kg' sejam tratados como o mesmo produto."""
    nome = " ".join(nome.split())
    return nome[:1].upper() + nome[1:]


def registrar_doacao(base, usuario, doador_id, nome, categoria, quantidade,
                     unidade, peso_kg, validade, lote):
    doador = por_id(base, "pessoas", doador_id)
    if doador is None or doador["tipo"] != "doador":
        raise RegraNegocioErro("Doador não encontrado.")
    if categoria not in CATEGORIAS:
        raise RegraNegocioErro("Categoria inválida.")
    if quantidade <= 0:
        raise RegraNegocioErro("A quantidade deve ser maior que zero.")
    if categoria in EXIGEM_VALIDADE and validade is None:
        raise RegraNegocioErro(f"Produtos da categoria {categoria} exigem validade.")
    if validade is not None and validade < date.today():
        raise RegraNegocioErro("Não é permitido receber produto já vencido.")

    produto = {
        "id": proximo_id(base, "produtos"),
        "nome": padronizar_nome(nome),
        "categoria": categoria,
        "quantidade": quantidade,
        "quantidade_inicial": quantidade,
        "unidade": unidade,
        "peso_kg": peso_kg,
        "validade": validade.isoformat() if validade else None,
        "lote": lote or "-",
        "doador_id": doador_id,
        "entrada": agora_iso(),
        "descartado": False,
    }
    base["produtos"].append(produto)
    mov = registrar_movimentacao(base, "entrada", produto["id"], quantidade,
                                 usuario["id"], pessoa_id=doador_id)
    return produto, mov


def registrar_movimentacao(base, tipo, produto_id, quantidade, usuario_id,
                           pessoa_id=None, solicitacao_id=None, data=None):
    mov = {
        "id": proximo_id(base, "movimentacoes"),
        "data": data or agora_iso(),
        "tipo": tipo,  # entrada | saida | descarte
        "produto_id": produto_id,
        "quantidade": quantidade,
        "usuario_id": usuario_id,
        "pessoa_id": pessoa_id,
        "solicitacao_id": solicitacao_id,
    }
    base["movimentacoes"].append(mov)
    return mov


def desfazer_doacao(base, produto_id):
    """Desfaz uma doação apenas se o lote ainda não teve nenhuma saída."""
    produto = por_id(base, "produtos", produto_id)
    if produto is None:
        raise RegraNegocioErro("Produto não encontrado.")
    movs = [m for m in base["movimentacoes"] if m["produto_id"] == produto_id]
    if any(m["tipo"] != "entrada" for m in movs):
        raise RegraNegocioErro("O lote já foi movimentado e não pode ser desfeito.")
    base["produtos"].remove(produto)
    for m in movs:
        base["movimentacoes"].remove(m)
    return produto


# ----------------------------------------------------------------------
# VALIDADE E DESCARTE
# ----------------------------------------------------------------------
def alertas_validade(base, dias=DIAS_ALERTA):
    """Lotes vencidos (dias < 0) e próximos do vencimento, por urgência."""
    alertas = []
    for p in base["produtos"]:
        if p["validade"] and p["quantidade"] > 0 and not p.get("descartado"):
            restante = dias_ate(p["validade"])
            if restante <= dias:
                alertas.append((p, restante))
    return merge_sort(alertas, chave=lambda a: a[1])


def descartar_vencidos(base, usuario):
    descartados = []
    for produto, restante in alertas_validade(base, dias=-1):
        registrar_movimentacao(base, "descarte", produto["id"],
                               produto["quantidade"], usuario["id"])
        descartados.append((produto["nome"], produto["lote"], produto["quantidade"]))
        produto["quantidade"] = 0
        produto["descartado"] = True
    return descartados


# ----------------------------------------------------------------------
# SOLICITAÇÕES (FILA FIFO)
# ----------------------------------------------------------------------
def criar_solicitacao(base, solicitante_id, nome_produto, quantidade, usuario,
                      justificativa=""):
    solicitante = por_id(base, "pessoas", solicitante_id)
    if solicitante is None or solicitante["tipo"] != "solicitante":
        raise RegraNegocioErro("Solicitante não encontrado.")
    disponivel = catalogo_disponivel(base).get(nome_produto, 0)
    if disponivel == 0:
        raise RegraNegocioErro("Produto indisponível no estoque.")
    if quantidade <= 0 or quantidade > disponivel:
        raise RegraNegocioErro(f"Quantidade inválida. Disponível: {disponivel}.")
    # Regra de acesso justo: uma solicitação pendente por produto e pessoa
    for s in base["solicitacoes"]:
        if (s["solicitante_id"] == solicitante_id and s["produto"] == nome_produto
                and s["status"] == "pendente"):
            raise RegraNegocioErro("Já existe uma solicitação pendente deste produto.")
    solicitacao = {
        "id": proximo_id(base, "solicitacoes"),
        "data": agora_iso(),
        "solicitante_id": solicitante_id,
        "produto": nome_produto,
        "quantidade": quantidade,
        "justificativa": justificativa,
        "status": "pendente",
        "registrada_por": usuario["id"],
        "avaliador_id": None,
        "data_avaliacao": None,
        "motivo": "",
    }
    base["solicitacoes"].append(solicitacao)
    return solicitacao


def fila_pendentes(base):
    """Monta a fila com as solicitações pendentes, por ordem de chegada."""
    fila = Fila()
    for s in merge_sort(base["solicitacoes"], chave=lambda x: x["data"]):
        if s["status"] == "pendente":
            fila.enfileirar(s["id"])
    return fila


def lotes_para_saida(base, nome_produto):
    """Critério PVPS (primeiro que vence, primeiro que sai)."""
    lotes = [p for p in base["produtos"]
             if p["nome"] == nome_produto and lote_valido(p)]
    return merge_sort(lotes, chave=lambda p: p["validade"] or "9999-12-31")


def avaliar_solicitacao(base, solicitacao_id, aprovar, usuario, motivo=""):
    fila = fila_pendentes(base)
    if fila.primeiro() != solicitacao_id:
        raise RegraNegocioErro("Avalie as solicitações na ordem da fila.")
    solicitacao = por_id(base, "solicitacoes", solicitacao_id)
    if aprovar:
        lotes = lotes_para_saida(base, solicitacao["produto"])
        if sum(l["quantidade"] for l in lotes) < solicitacao["quantidade"]:
            raise RegraNegocioErro("Estoque insuficiente. Reprove ou aguarde doações.")
        falta = solicitacao["quantidade"]
        for lote in lotes:  # baixa nos lotes que vencem primeiro
            retirar = min(falta, lote["quantidade"])
            lote["quantidade"] -= retirar
            registrar_movimentacao(base, "saida", lote["id"], retirar, usuario["id"],
                                   pessoa_id=solicitacao["solicitante_id"],
                                   solicitacao_id=solicitacao_id)
            falta -= retirar
            if falta == 0:
                break
        solicitacao["status"] = "aprovada"
    else:
        if not motivo:
            raise RegraNegocioErro("Informe o motivo da reprovação.")
        solicitacao["status"] = "reprovada"
    solicitacao["avaliador_id"] = usuario["id"]
    solicitacao["data_avaliacao"] = agora_iso()
    solicitacao["motivo"] = motivo
    fila.desenfileirar()
    return solicitacao


def solicitacoes_da_pessoa(base, pessoa_id):
    return [s for s in base["solicitacoes"] if s["solicitante_id"] == pessoa_id]


def posicao_na_fila(base, solicitacao_id):
    itens = fila_pendentes(base).itens()
    return itens.index(solicitacao_id) + 1 if solicitacao_id in itens else None


# ----------------------------------------------------------------------
# RELATÓRIOS
# ----------------------------------------------------------------------
def _no_periodo(data_iso, inicio, fim):
    dia = data_iso[:10]
    return inicio.isoformat() <= dia <= fim.isoformat()


def relatorio_movimentacoes(base, inicio, fim):
    """Entradas, saídas e descartes do período, com totais."""
    linhas, totais = [], {"entrada": 0, "saida": 0, "descarte": 0}
    for m in merge_sort(base["movimentacoes"], chave=lambda x: x["data"]):
        if _no_periodo(m["data"], inicio, fim):
            produto = por_id(base, "produtos", m["produto_id"])
            linhas.append((m, produto))
            totais[m["tipo"]] += m["quantidade"]
    return linhas, totais


def relatorio_mais_solicitados(base, inicio, fim, limite=10):
    """Ranking dos produtos mais solicitados (contagem + merge sort)."""
    contagem = {}
    for s in base["solicitacoes"]:
        if _no_periodo(s["data"], inicio, fim):
            item = contagem.setdefault(s["produto"], {"pedidos": 0, "unidades": 0})
            item["pedidos"] += 1
            item["unidades"] += s["quantidade"]
    ranking = [(nome, d["pedidos"], d["unidades"]) for nome, d in contagem.items()]
    ranking = merge_sort(ranking, chave=lambda r: (r[1], r[2]), decrescente=True)
    return ranking[:limite]


def relatorio_doacoes_por_doador(base, inicio, fim):
    """Total doado por doador no período, com participação percentual."""
    por_doador = {}
    for m in base["movimentacoes"]:
        if m["tipo"] == "entrada" and _no_periodo(m["data"], inicio, fim):
            por_doador[m["pessoa_id"]] = por_doador.get(m["pessoa_id"], 0) + m["quantidade"]
    total = sum(por_doador.values())
    linhas = []
    for pessoa_id, qtd in por_doador.items():
        doador = por_id(base, "pessoas", pessoa_id)
        percentual = (qtd / total * 100) if total else 0
        linhas.append((doador["nome"] if doador else "?", qtd, percentual))
    return merge_sort(linhas, chave=lambda l: l[1], decrescente=True), total


def relatorio_doacoes_por_periodo(base, inicio, fim):
    """Unidades doadas por mês (AAAA-MM) dentro do período."""
    por_mes = {}
    for m in base["movimentacoes"]:
        if m["tipo"] == "entrada" and _no_periodo(m["data"], inicio, fim):
            mes = m["data"][:7]
            por_mes[mes] = por_mes.get(mes, 0) + m["quantidade"]
    return merge_sort(list(por_mes.items()), chave=lambda x: x[0])


def indicadores(base):
    """Indicadores gerais calculados a partir dos dados (matemática aplicada)."""
    entradas = sum(m["quantidade"] for m in base["movimentacoes"] if m["tipo"] == "entrada")
    saidas = sum(m["quantidade"] for m in base["movimentacoes"] if m["tipo"] == "saida")
    descartes = sum(m["quantidade"] for m in base["movimentacoes"] if m["tipo"] == "descarte")
    avaliadas = [s for s in base["solicitacoes"] if s["status"] != "pendente"]
    aprovadas = [s for s in avaliadas if s["status"] == "aprovada"]
    esperas = []
    for s in avaliadas:  # tempo de espera em dias entre pedido e avaliação
        esperas.append((date.fromisoformat(s["data_avaliacao"][:10])
                        - date.fromisoformat(s["data"][:10])).days)
    return {
        "entradas": entradas,
        "saidas": saidas,
        "descartes": descartes,
        "em_estoque": entradas - saidas - descartes,
        "taxa_aproveitamento": (saidas / entradas * 100) if entradas else 0.0,
        "taxa_perda": (descartes / entradas * 100) if entradas else 0.0,
        "taxa_aprovacao": (len(aprovadas) / len(avaliadas) * 100) if avaliadas else 0.0,
        "espera_media_dias": (sum(esperas) / len(esperas)) if esperas else 0.0,
        "pendentes": fila_pendentes(base).tamanho(),
    }


def periodo_padrao():
    """Últimos 30 dias."""
    hoje = date.today()
    return hoje - timedelta(days=30), hoje
