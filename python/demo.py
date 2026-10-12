"""
demo.py
Cria uma base de demonstração com dados fictícios, usada nos testes e na
apresentação do sistema. Execute: python main.py --demo
"""

from datetime import date, datetime, timedelta

import dados
import seguranca
import servicos as srv


def _data(dias_atras, hora=10):
    momento = datetime.combine(date.today() - timedelta(days=dias_atras),
                               datetime.min.time()).replace(hour=hora)
    return momento.strftime("%Y-%m-%dT%H:%M:%S")


def criar_base_demo():
    base = dados.base_vazia()
    admin = seguranca.criar_usuario(base, "Administrador do Sistema", "admin",
                                    "admin123", "administrador",
                                    "Nome da instituição?", "compartilha")
    voluntario = seguranca.criar_usuario(base, "Marina Souza", "marina", "vol2025",
                                         "voluntario", "Cidade natal?", "sorocaba")

    # Pessoas fictícias (documentos gerados apenas para demonstração)
    doadores = [
        ("Mercado Bom Preço Ltda.", "12345678000190"),
        ("Paróquia São José", "98765432000110"),
        ("Carlos Henrique Lima", "11122233344"),
    ]
    solicitantes = [
        ("Ana Paula Ferreira", "55566677788"),
        ("José Roberto Alves", "99988877766"),
        ("Lúcia Mendes", "44433322211"),
    ]
    for nome, doc in doadores:
        srv.cadastrar_pessoa(base, nome, doc, "(15) 3200-0000", "", "doador")
    for nome, doc in solicitantes:
        srv.cadastrar_pessoa(base, nome, doc, "(15) 99999-0000", "", "solicitante")
    ana = base["pessoas"][3]
    seguranca.criar_usuario(base, ana["nome"], "ana", "ana2025", "solicitante",
                            "Nome do primeiro animal?", "rex", pessoa_id=ana["id"])

    hoje = date.today()
    # (doador, nome, categoria, qtd, unidade, peso, validade, lote, dias atrás)
    doacoes = [
        (1, "Arroz 5kg", "Alimentos", 40, "pct", 200, hoje + timedelta(days=180), "A01", 45),
        (1, "Feijão 1kg", "Alimentos", 60, "pct", 60, hoje + timedelta(days=20), "F07", 40),
        (2, "Leite em pó 400g", "Alimentos", 25, "lata", 10, hoje + timedelta(days=12), "L22", 30),
        (2, "Sabonete", "Higiene", 80, "un", 7.2, hoje + timedelta(days=400), "S10", 28),
        (3, "Paracetamol 500mg", "Medicamentos", 15, "cx", 0.6, hoje + timedelta(days=90), "P55", 20),
        (3, "Carrinho de brinquedo", "Brinquedos", 12, "un", 3, None, "", 15),
        (1, "Feijão 1kg", "Alimentos", 30, "pct", 30, hoje + timedelta(days=150), "F09", 10),
        (2, "Agasalho infantil", "Vestuário", 20, "un", 8, None, "", 5),
    ]
    for d, nome, cat, qtd, un, peso, val, lote, atras in doacoes:
        produto, mov = srv.registrar_doacao(base, voluntario, d, nome, cat, qtd, un,
                                            peso, val, lote)
        produto["entrada"] = mov["data"] = _data(atras)

    # Um lote que venceu enquanto estava no estoque (para o alerta e o descarte)
    produto, mov = srv.registrar_doacao(base, voluntario, 1, "Biscoito Recheado",
                                        "Alimentos", 18, "pct", 2.5,
                                        hoje + timedelta(days=1), "B03")
    produto["validade"] = (hoje - timedelta(days=3)).isoformat()
    produto["entrada"] = mov["data"] = _data(60)

    # Solicitações: algumas já avaliadas, outras na fila
    pedidos = [(4, "Arroz 5kg", 4, 25), (5, "Feijão 1kg", 15, 22),
               (6, "Leite em pó 400g", 6, 18), (4, "Sabonete", 4, 12),
               (5, "Paracetamol 500mg", 2, 8)]
    for pessoa_id, produto_nome, qtd, atras in pedidos:
        s = srv.criar_solicitacao(base, pessoa_id, produto_nome, qtd, voluntario)
        s["data"] = _data(atras, hora=9)
    resultados = [(True, ""), (True, ""), (True, ""), (False, "Item já entregue na semana."),
                  (True, "")]
    for (aprovar, motivo), atras in zip(resultados, [24, 20, 17, 11, 6]):
        sid = srv.fila_pendentes(base).primeiro()
        s = srv.avaliar_solicitacao(base, sid, aprovar, admin, motivo)
        s["data_avaliacao"] = _data(atras, hora=15)
        for m in base["movimentacoes"]:
            if m["solicitacao_id"] == sid:
                m["data"] = s["data_avaliacao"]

    for pessoa_id, produto_nome, qtd, atras in [(6, "Arroz 5kg", 2, 2),
                                                (4, "Feijão 1kg", 3, 1),
                                                (5, "Agasalho infantil", 2, 0)]:
        s = srv.criar_solicitacao(base, pessoa_id, produto_nome, qtd, voluntario)
        s["data"] = _data(atras, hora=8)

    # mantém as movimentações em ordem de id (necessário para a busca binária)
    base["movimentacoes"].sort(key=lambda m: m["id"])
    for usuario in base["usuarios"]:
        usuario["tentativas"] = 0
    return base


if __name__ == "__main__":
    dados.salvar(criar_base_demo())
    print("Base de demonstração criada.")
