"""
telas.py
Telas (menus) do sistema. Cada tela lê os dados do usuário, chama as
regras de negócio de servicos.py e grava a base com dados.salvar().
"""

from datetime import datetime

import dados
import seguranca
import servicos as srv
from estruturas import Pilha
from interface import (cabecalho, pausar, mensagem, menu, ler_texto, ler_inteiro,
                       ler_decimal, ler_data, confirmar, tabela, para_texto,
                       dias_ate, percentual, FORMATO_DATA)
from servicos import RegraNegocioErro

# Pilha com as ações realizadas na sessão (permite desfazer a última doação)
acoes_sessao = Pilha(limite=20)


def registrar_acao(descricao, tipo="info", dados_acao=None):
    acoes_sessao.empilhar({"hora": datetime.now().strftime("%H:%M"),
                           "descricao": descricao, "tipo": tipo,
                           "dados": dados_acao})


# ======================================================================
# LOGIN E RECUPERAÇÃO DE SENHA
# ======================================================================
def tela_login(base):
    while True:
        cabecalho("Acesso ao sistema")
        opcao = menu([("1", "Entrar"), ("2", "Esqueci minha senha"), ("0", "Sair")])
        if opcao == "1":
            login = ler_texto("Login")
            senha = seguranca_ler_senha("Senha")
            usuario, msg = seguranca.autenticar(base, login, senha)
            dados.salvar(base)  # grava tentativas/bloqueio
            mensagem(msg, "ok" if usuario else "erro")
            pausar()
            if usuario:
                return usuario
        elif opcao == "2":
            tela_recuperar_senha(base)
        elif opcao == "0":
            return None
        else:
            mensagem("Opção inválida.", "erro")
            pausar()


def seguranca_ler_senha(rotulo):
    """Usa getpass (não mostra a senha) quando há terminal disponível."""
    import sys
    if sys.stdin.isatty():
        import getpass
        return getpass.getpass(f"{rotulo}: ")
    return input(f"{rotulo}: ")


def tela_recuperar_senha(base):
    cabecalho("Recuperação de senha")
    login = ler_texto("Login")
    usuario = next((u for u in base["usuarios"] if u["login"] == login), None)
    if usuario is None:
        mensagem("Usuário não encontrado.", "erro")
        pausar()
        return
    print(f"Pergunta de segurança: {usuario['pergunta']}")
    resposta = ler_texto("Resposta")
    nova = seguranca_ler_senha("Nova senha")
    ok, msg = seguranca.redefinir_senha(base, login, resposta, nova)
    if ok:
        dados.salvar(base)
    mensagem(msg, "ok" if ok else "erro")
    pausar()


# ======================================================================
# CADASTROS
# ======================================================================
def tela_cadastrar_pessoa(base, usuario, tipo):
    cabecalho(f"Cadastro de {tipo}", usuario)
    nome = ler_texto("Nome completo / Razão social", minimo=3)
    documento = ler_texto("CPF ou CNPJ (somente números)")
    telefone = ler_texto("Telefone", obrigatorio=False)
    email = ler_texto("E-mail", obrigatorio=False)
    try:
        pessoa = srv.cadastrar_pessoa(base, nome, documento, telefone, email, tipo)
    except RegraNegocioErro as erro:
        mensagem(str(erro), "erro")
        pausar()
        return None
    if tipo == "solicitante" and confirmar("Criar acesso ao sistema para este solicitante?"):
        criar_acesso(base, nome, "solicitante", pessoa["id"])
    dados.salvar(base)
    registrar_acao(f"Cadastro do {tipo} {pessoa['nome']} (cód. {pessoa['id']})")
    mensagem(f"{tipo.capitalize()} cadastrado com o código {pessoa['id']}.", "ok")
    pausar()
    return pessoa


def criar_acesso(base, nome, perfil, pessoa_id=None):
    while True:
        login = ler_texto("Login de acesso", minimo=3)
        senha = seguranca_ler_senha("Senha (6+ caracteres, letras e números)")
        pergunta = ler_texto("Pergunta de segurança")
        resposta = ler_texto("Resposta da pergunta")
        try:
            seguranca.criar_usuario(base, nome, login, senha, perfil,
                                    pergunta, resposta, pessoa_id)
            mensagem(f"Acesso '{login}' criado com perfil {perfil}.", "ok")
            return
        except ValueError as erro:
            mensagem(str(erro), "erro")
            if not confirmar("Tentar novamente?"):
                return


def tela_cadastrar_usuario(base, usuario):
    cabecalho("Cadastro de funcionário / voluntário", usuario)
    nome = ler_texto("Nome completo", minimo=3)
    print("Perfil: 1 - Administrador | 2 - Voluntário")
    perfil = "administrador" if ler_inteiro("Opção", 1, 2) == 1 else "voluntario"
    criar_acesso(base, nome, perfil)
    dados.salvar(base)
    registrar_acao(f"Cadastro de usuário {nome} ({perfil})")
    pausar()


def tela_listar_pessoas(base, usuario):
    cabecalho("Doadores e solicitantes", usuario)
    linhas = [(p["id"], p["tipo"], p["nome"], p["documento"], p["telefone"])
              for p in base["pessoas"]]
    tabela([("Cód", 5), ("Tipo", 12), ("Nome", 28), ("Documento", 15),
            ("Telefone", 15)], linhas)
    pausar()


def tela_gerenciar_usuarios(base, usuario):
    while True:
        cabecalho("Usuários do sistema", usuario)
        linhas = [(u["id"], u["login"], u["nome"], u["perfil"],
                   "BLOQUEADO" if u["bloqueado"] else "ativo")
                  for u in base["usuarios"]]
        tabela([("Cód", 5), ("Login", 14), ("Nome", 26), ("Perfil", 14),
                ("Situação", 10)], linhas)
        print()
        opcao = menu([("1", "Cadastrar funcionário/voluntário"),
                      ("2", "Desbloquear usuário"), ("0", "Voltar")])
        if opcao == "1":
            tela_cadastrar_usuario(base, usuario)
        elif opcao == "2":
            codigo = ler_inteiro("Código do usuário", 1)
            alvo = srv.por_id(base, "usuarios", codigo)
            if alvo:
                alvo["bloqueado"], alvo["tentativas"] = False, 0
                dados.salvar(base)
                mensagem("Usuário desbloqueado.", "ok")
            else:
                mensagem("Usuário não encontrado.", "erro")
            pausar()
        elif opcao == "0":
            return


# ======================================================================
# DOAÇÕES E ESTOQUE
# ======================================================================
def escolher_pessoa(base, tipo):
    pessoas = srv.pessoas_do_tipo(base, tipo)
    if not pessoas:
        mensagem(f"Nenhum {tipo} cadastrado. Cadastre antes de continuar.", "alerta")
        return None
    tabela([("Cód", 5), ("Nome", 35), ("Documento", 15)],
           [(p["id"], p["nome"], p["documento"]) for p in pessoas])
    codigo = ler_inteiro(f"\nCódigo do {tipo}", 1)
    pessoa = srv.por_id(base, "pessoas", codigo)
    if pessoa is None or pessoa["tipo"] != tipo:
        mensagem(f"{tipo.capitalize()} não encontrado.", "erro")
        return None
    return pessoa


def tela_registrar_doacao(base, usuario):
    cabecalho("Registrar doação (entrada de produto)", usuario)
    doador = escolher_pessoa(base, "doador")
    if doador is None:
        pausar()
        return
    print()
    for i, categoria in enumerate(srv.CATEGORIAS, 1):
        print(f"  {i} - {categoria}")
    categoria = srv.CATEGORIAS[ler_inteiro("Categoria", 1, len(srv.CATEGORIAS)) - 1]
    nome = ler_texto("Nome do produto", minimo=2)
    quantidade = ler_inteiro("Quantidade", 1)
    unidade = ler_texto("Unidade (un, pct, cx, kg...)")
    peso = ler_decimal("Peso total aproximado (kg)")
    exige = categoria in srv.EXIGEM_VALIDADE
    validade = ler_data("Validade", permitir_vazio=not exige, permitir_passado=False)
    lote = ler_texto("Lote", obrigatorio=False)
    try:
        produto, _ = srv.registrar_doacao(base, usuario, doador["id"], nome, categoria,
                                          quantidade, unidade, peso, validade, lote)
    except RegraNegocioErro as erro:
        mensagem(str(erro), "erro")
        pausar()
        return
    dados.salvar(base)
    registrar_acao(f"Doação de {quantidade} {unidade} de {produto['nome']} "
                   f"por {doador['nome']}", "doacao", produto["id"])
    mensagem(f"Doação registrada. Lote interno nº {produto['id']}.", "ok")
    pausar()


def linhas_estoque(produtos):
    linhas = []
    for p in produtos:
        situacao = "-"
        if p["validade"]:
            dias = dias_ate(p["validade"])
            situacao = "VENCIDO" if dias < 0 else f"{dias} dia(s)"
        linhas.append((p["id"], p["nome"], p["categoria"],
                       f"{p['quantidade']} {p['unidade']}",
                       para_texto(p["validade"]), situacao))
    return linhas


COLUNAS_ESTOQUE = [("Lote", 5), ("Produto", 24), ("Categoria", 13),
                   ("Saldo", 10), ("Validade", 11), ("Vence em", 10)]


def tela_estoque(base, usuario):
    while True:
        cabecalho("Controle de estoque", usuario)
        alertas = srv.alertas_validade(base)
        vencidos = sum(1 for _, d in alertas if d < 0)
        if alertas:
            mensagem(f"{len(alertas)} lote(s) com alerta de validade "
                     f"({vencidos} vencido(s)).", "alerta")
            print()
        opcao = menu([("1", "Listar estoque (ordem alfabética)"),
                      ("2", "Busca com filtros"),
                      ("3", "Alertas de validade"),
                      ("4", "Descartar produtos vencidos"),
                      ("0", "Voltar")])
        if opcao == "1":
            cabecalho("Estoque disponível", usuario)
            tabela(COLUNAS_ESTOQUE, linhas_estoque(srv.filtrar_produtos(base)))
            pausar()
        elif opcao == "2":
            tela_busca_filtros(base, usuario)
        elif opcao == "3":
            cabecalho(f"Alertas de validade (até {srv.DIAS_ALERTA} dias)", usuario)
            tabela(COLUNAS_ESTOQUE, linhas_estoque([p for p, _ in alertas]))
            pausar()
        elif opcao == "4":
            tela_descartar(base, usuario)
        elif opcao == "0":
            return


def tela_busca_filtros(base, usuario):
    cabecalho("Busca de produtos com filtros", usuario)
    print("Deixe em branco os filtros que não quiser usar.\n")
    prefixo = ler_texto("Nome começa com", obrigatorio=False)
    print("Categorias: 0 - Todas | " +
          " | ".join(f"{i} - {c}" for i, c in enumerate(srv.CATEGORIAS[:3], 1)))
    print("            " +
          " | ".join(f"{i} - {c}" for i, c in enumerate(srv.CATEGORIAS[3:], 4)))
    indice = ler_inteiro("Categoria", 0, len(srv.CATEGORIAS), permitir_vazio=True)
    categoria = srv.CATEGORIAS[indice - 1] if indice else None
    vence_em = ler_inteiro("Vence em até quantos dias", 0, permitir_vazio=True)
    resultado = srv.filtrar_produtos(base, prefixo, categoria, vence_em)
    print()
    tabela(COLUNAS_ESTOQUE, linhas_estoque(resultado))
    pausar()


def tela_descartar(base, usuario):
    cabecalho("Descarte de produtos vencidos", usuario)
    vencidos = [p for p, d in srv.alertas_validade(base) if d < 0]
    if not vencidos:
        mensagem("Não há produtos vencidos no estoque.", "ok")
        pausar()
        return
    tabela(COLUNAS_ESTOQUE, linhas_estoque(vencidos))
    print("\nOs itens serão baixados do estoque e devem ser levados a um ponto")
    print("de coleta para descarte adequado (logística reversa).")
    if confirmar("Confirmar descarte?"):
        descartados = srv.descartar_vencidos(base, usuario)
        dados.salvar(base)
        registrar_acao(f"Descarte de {len(descartados)} lote(s) vencido(s)")
        mensagem(f"{len(descartados)} lote(s) descartado(s).", "ok")
    pausar()


# ======================================================================
# SOLICITAÇÕES
# ======================================================================
def tela_nova_solicitacao(base, usuario, solicitante_id=None):
    cabecalho("Nova solicitação de produto", usuario)
    if solicitante_id is None:  # voluntário registrando para alguém
        pessoa = escolher_pessoa(base, "solicitante")
        if pessoa is None:
            pausar()
            return
        solicitante_id = pessoa["id"]
        print()
    catalogo = srv.catalogo_disponivel(base)
    if not catalogo:
        mensagem("Não há produtos disponíveis no momento.", "alerta")
        pausar()
        return
    nomes = list(catalogo.keys())
    tabela([("Nº", 4), ("Produto disponível", 34), ("Quantidade", 10)],
           [(i, n, catalogo[n]) for i, n in enumerate(nomes, 1)])
    escolha = ler_inteiro("\nNúmero do produto", 1, len(nomes))
    quantidade = ler_inteiro("Quantidade desejada", 1)
    justificativa = ler_texto("Justificativa (opcional)", obrigatorio=False)
    try:
        s = srv.criar_solicitacao(base, solicitante_id, nomes[escolha - 1],
                                  quantidade, usuario, justificativa)
    except RegraNegocioErro as erro:
        mensagem(str(erro), "erro")
        pausar()
        return
    dados.salvar(base)
    registrar_acao(f"Solicitação nº {s['id']} de {quantidade} {s['produto']}")
    mensagem(f"Solicitação nº {s['id']} registrada. Posição na fila: "
             f"{srv.posicao_na_fila(base, s['id'])}.", "ok")
    pausar()


def tela_avaliar_solicitacoes(base, usuario):
    while True:
        cabecalho("Fila de solicitações (ordem de chegada)", usuario)
        fila = srv.fila_pendentes(base)
        if fila.vazia():
            mensagem("Não há solicitações pendentes.", "ok")
            pausar()
            return
        linhas = []
        for pos, sid in enumerate(fila.itens(), 1):
            s = srv.por_id(base, "solicitacoes", sid)
            pessoa = srv.por_id(base, "pessoas", s["solicitante_id"])
            disp = srv.catalogo_disponivel(base).get(s["produto"], 0)
            linhas.append((pos, s["id"], para_texto(s["data"]), pessoa["nome"],
                           s["produto"], s["quantidade"], disp))
        tabela([("Pos", 4), ("Nº", 4), ("Data", 11), ("Solicitante", 20),
                ("Produto", 18), ("Qtd", 5), ("Disp.", 6)], linhas)
        atual = srv.por_id(base, "solicitacoes", fila.primeiro())
        print(f"\nPróxima da fila: nº {atual['id']} – {atual['quantidade']} x "
              f"{atual['produto']}")
        if atual["justificativa"]:
            print(f"Justificativa: {atual['justificativa']}")
        opcao = menu([("1", "Aprovar"), ("2", "Reprovar"), ("0", "Voltar")])
        if opcao == "0":
            return
        if opcao not in ("1", "2"):
            continue
        motivo = "" if opcao == "1" else ler_texto("Motivo da reprovação")
        try:
            srv.avaliar_solicitacao(base, atual["id"], opcao == "1", usuario, motivo)
        except RegraNegocioErro as erro:
            mensagem(str(erro), "erro")
            pausar()
            continue
        dados.salvar(base)
        situacao = "aprovada" if opcao == "1" else "reprovada"
        registrar_acao(f"Solicitação nº {atual['id']} {situacao}")
        mensagem(f"Solicitação {situacao}.", "ok")
        pausar()


def tela_minhas_solicitacoes(base, usuario):
    cabecalho("Minhas solicitações", usuario)
    linhas = []
    for s in srv.solicitacoes_da_pessoa(base, usuario["pessoa_id"]):
        situacao = s["status"]
        if situacao == "pendente":
            situacao += f" (fila: {srv.posicao_na_fila(base, s['id'])}º)"
        linhas.append((s["id"], para_texto(s["data"]), s["produto"],
                       s["quantidade"], situacao, s["motivo"]))
    tabela([("Nº", 4), ("Data", 11), ("Produto", 20), ("Qtd", 5),
            ("Situação", 21), ("Observação", 30)], linhas)
    pausar()


def tela_historico_solicitante(base, usuario):
    cabecalho("Histórico de atendimentos por solicitante", usuario)
    pessoa = escolher_pessoa(base, "solicitante")
    if pessoa:
        cabecalho(f"Atendimentos de {pessoa['nome']}", usuario)
        linhas = [(s["id"], para_texto(s["data"]), s["produto"], s["quantidade"],
                   s["status"], para_texto(s["data_avaliacao"]))
                  for s in srv.solicitacoes_da_pessoa(base, pessoa["id"])]
        tabela([("Nº", 4), ("Pedido", 11), ("Produto", 22), ("Qtd", 5),
                ("Situação", 10), ("Avaliação", 11)], linhas)
    pausar()


# ======================================================================
# RELATÓRIOS
# ======================================================================
def ler_periodo():
    inicio_padrao, fim_padrao = srv.periodo_padrao()
    print("Período (ENTER = últimos 30 dias)")
    inicio = ler_data("Data inicial", permitir_vazio=True) or inicio_padrao
    fim = ler_data("Data final", permitir_vazio=True) or fim_padrao
    if inicio > fim:
        inicio, fim = fim, inicio
    return inicio, fim


def tela_relatorios(base, usuario):
    while True:
        cabecalho("Relatórios", usuario)
        opcao = menu([("1", "Entradas e saídas por período"),
                      ("2", "Produtos mais solicitados"),
                      ("3", "Doações por doador"),
                      ("4", "Doações por período (mensal)"),
                      ("5", "Indicadores gerais"),
                      ("6", "Histórico de atendimentos por solicitante"),
                      ("0", "Voltar")])
        if opcao == "0":
            return
        if opcao == "6":
            tela_historico_solicitante(base, usuario)
            continue
        if opcao == "5":
            relatorio_indicadores(base, usuario)
            continue
        if opcao not in ("1", "2", "3", "4"):
            continue
        inicio, fim = ler_periodo()
        titulo = f"{inicio.strftime(FORMATO_DATA)} a {fim.strftime(FORMATO_DATA)}"
        if opcao == "1":
            cabecalho(f"Movimentações – {titulo}", usuario)
            linhas, totais = srv.relatorio_movimentacoes(base, inicio, fim)
            tabela([("Data", 11), ("Tipo", 9), ("Produto", 24), ("Lote", 5),
                    ("Qtd", 6)],
                   [(para_texto(m["data"]), m["tipo"],
                     p["nome"] if p else "-", m["produto_id"], m["quantidade"])
                    for m, p in linhas])
            print(f"\nEntradas: {totais['entrada']} | Saídas: {totais['saida']} | "
                  f"Descartes: {totais['descarte']}")
        elif opcao == "2":
            cabecalho(f"Mais solicitados – {titulo}", usuario)
            ranking = srv.relatorio_mais_solicitados(base, inicio, fim)
            tabela([("Pos", 4), ("Produto", 30), ("Pedidos", 8), ("Unidades", 9)],
                   [(i, n, p, u) for i, (n, p, u) in enumerate(ranking, 1)])
        elif opcao == "3":
            cabecalho(f"Doações por doador – {titulo}", usuario)
            linhas, total = srv.relatorio_doacoes_por_doador(base, inicio, fim)
            tabela([("Doador", 32), ("Unidades", 9), ("Participação", 12)],
                   [(n, q, percentual(pct)) for n, q, pct in linhas])
            print(f"\nTotal doado no período: {total} unidade(s)")
        elif opcao == "4":
            cabecalho(f"Doações por mês – {titulo}", usuario)
            dados_mes = srv.relatorio_doacoes_por_periodo(base, inicio, fim)
            maior = max((q for _, q in dados_mes), default=0)
            for mes, qtd in dados_mes:
                barra = "#" * int(qtd / maior * 40) if maior else ""
                print(f"{mes[5:]}/{mes[:4]}  {str(qtd).rjust(5)}  {barra}")
            if not dados_mes:
                mensagem("Nenhuma doação no período.")
        pausar()


def relatorio_indicadores(base, usuario):
    cabecalho("Indicadores gerais", usuario)
    ind = srv.indicadores(base)
    print(f"Unidades recebidas ............ {ind['entradas']}")
    print(f"Unidades distribuídas ......... {ind['saidas']}")
    print(f"Unidades descartadas .......... {ind['descartes']}")
    print(f"Saldo em estoque .............. {ind['em_estoque']}")
    print(f"Taxa de aproveitamento ........ {percentual(ind['taxa_aproveitamento'])}")
    print(f"Taxa de perda por vencimento .. {percentual(ind['taxa_perda'])}")
    print(f"Taxa de aprovação ............. {percentual(ind['taxa_aprovacao'])}")
    print(f"Espera média até avaliação .... {str(round(ind['espera_media_dias'], 1)).replace('.', ',')} dia(s)")
    print(f"Solicitações na fila .......... {ind['pendentes']}")
    pausar()


# ======================================================================
# SISTEMA (BACKUP E AÇÕES DA SESSÃO)
# ======================================================================
def tela_backup(base, usuario):
    cabecalho("Backups automáticos", usuario)
    backups = dados.listar_backups()
    print(f"Um backup é gerado a cada gravação (mantidos os {dados.MAX_BACKUPS} "
          f"mais recentes).\n")
    for i, nome in enumerate(backups, 1):
        # nome no formato base_AAAAMMDD_HHMMSS_micro.json
        data, hora = nome[5:13], nome[14:20]
        print(f"  {i} - {data[6:]}/{data[4:6]}/{data[:4]} às "
              f"{hora[:2]}:{hora[2:4]}:{hora[4:]}  ({nome})")
    if backups and confirmar("\nRestaurar algum backup?"):
        indice = ler_inteiro("Número do backup", 1, len(backups))
        dados.restaurar_backup(backups[indice - 1])
        base.clear()
        base.update(dados.carregar())
        mensagem("Backup restaurado.", "ok")
    pausar()


def tela_acoes_sessao(base, usuario):
    cabecalho("Últimas ações da sessão (pilha)", usuario)
    acoes = acoes_sessao.itens()
    if not acoes:
        mensagem("Nenhuma ação registrada nesta sessão.")
        pausar()
        return
    for i, acao in enumerate(acoes, 1):
        print(f"  {i}. [{acao['hora']}] {acao['descricao']}")
    topo = acoes_sessao.topo()
    if topo["tipo"] == "doacao" and confirmar("\nDesfazer a última doação?"):
        try:
            produto = srv.desfazer_doacao(base, topo["dados"])
            acoes_sessao.desempilhar()
            dados.salvar(base)
            mensagem(f"Doação de {produto['nome']} desfeita.", "ok")
        except RegraNegocioErro as erro:
            mensagem(str(erro), "erro")
    pausar()


def tela_alterar_senha(base, usuario):
    cabecalho("Alterar senha", usuario)
    atual = seguranca_ler_senha("Senha atual")
    if not seguranca.conferir(atual, usuario["senha_hash"], usuario["sal"]):
        mensagem("Senha atual incorreta.", "erro")
    else:
        nova = seguranca_ler_senha("Nova senha")
        if seguranca.senha_forte(nova):
            usuario["senha_hash"], usuario["sal"] = seguranca.gerar_hash(nova)
            dados.salvar(base)
            mensagem("Senha alterada.", "ok")
        else:
            mensagem("A senha deve ter 6+ caracteres, com letras e números.", "erro")
    pausar()


# ======================================================================
# MENUS POR PERFIL
# ======================================================================
def menu_principal(base, usuario):
    """Monta o menu de acordo com o perfil (controle de acesso)."""
    perfil = usuario["perfil"]
    while True:
        cabecalho("Menu principal", usuario)
        if perfil == "solicitante":
            opcoes = [("1", "Ver produtos disponíveis"),
                      ("2", "Fazer solicitação"),
                      ("3", "Minhas solicitações"),
                      ("9", "Alterar senha"), ("0", "Sair")]
        else:
            opcoes = [("1", "Cadastrar doador"),
                      ("2", "Cadastrar solicitante"),
                      ("3", "Listar doadores e solicitantes"),
                      ("4", "Registrar doação"),
                      ("5", "Controle de estoque"),
                      ("6", "Registrar solicitação"),
                      ("7", "Últimas ações / desfazer")]
            if perfil == "administrador":
                opcoes += [("8", "Avaliar solicitações (fila)"),
                           ("R", "Relatórios"),
                           ("U", "Usuários"),
                           ("B", "Backups")]
            opcoes += [("9", "Alterar senha"), ("0", "Sair")]

        if perfil == "administrador":
            pendentes = srv.fila_pendentes(base).tamanho()
            if pendentes:
                mensagem(f"{pendentes} solicitação(ões) aguardando avaliação.", "alerta")
                print()
        opcao = menu(opcoes).upper()
        validas = [c for c, _ in opcoes]
        if opcao not in validas:
            mensagem("Opção inválida.", "erro")
            pausar()
            continue
        if opcao == "0":
            return
        if opcao == "9":
            tela_alterar_senha(base, usuario)
            continue

        if perfil == "solicitante":
            if opcao == "1":
                cabecalho("Produtos disponíveis", usuario)
                catalogo = srv.catalogo_disponivel(base)
                tabela([("Produto", 34), ("Quantidade", 10)], list(catalogo.items()))
                pausar()
            elif opcao == "2":
                tela_nova_solicitacao(base, usuario, usuario["pessoa_id"])
            elif opcao == "3":
                tela_minhas_solicitacoes(base, usuario)
            continue

        acoes = {
            "1": lambda: tela_cadastrar_pessoa(base, usuario, "doador"),
            "2": lambda: tela_cadastrar_pessoa(base, usuario, "solicitante"),
            "3": lambda: tela_listar_pessoas(base, usuario),
            "4": lambda: tela_registrar_doacao(base, usuario),
            "5": lambda: tela_estoque(base, usuario),
            "6": lambda: tela_nova_solicitacao(base, usuario),
            "7": lambda: tela_acoes_sessao(base, usuario),
            "8": lambda: tela_avaliar_solicitacoes(base, usuario),
            "R": lambda: tela_relatorios(base, usuario),
            "U": lambda: tela_gerenciar_usuarios(base, usuario),
            "B": lambda: tela_backup(base, usuario),
        }
        acoes[opcao]()
