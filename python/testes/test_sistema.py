"""
Testes automatizados (unittest) das estruturas de dados e regras de negócio.
Execute na pasta do projeto:  python -m unittest discover -s testes -v
"""

import os
import sys
import unittest
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import seguranca  # noqa: E402
import servicos as srv  # noqa: E402
from demo import criar_base_demo  # noqa: E402
from estruturas import Fila, Pilha, ArvoreBST, merge_sort, busca_binaria  # noqa: E402
from servicos import RegraNegocioErro  # noqa: E402


class TesteEstruturas(unittest.TestCase):
    def test_fila_respeita_ordem_de_chegada(self):
        fila = Fila()
        for x in (10, 20, 30):
            fila.enfileirar(x)
        self.assertEqual(fila.desenfileirar(), 10)
        self.assertEqual(fila.primeiro(), 20)
        self.assertEqual(fila.tamanho(), 2)

    def test_pilha_devolve_ultimo_inserido(self):
        pilha = Pilha(limite=2)
        for x in ("a", "b", "c"):
            pilha.empilhar(x)
        self.assertEqual(pilha.itens(), ["c", "b"])  # limite descarta o mais antigo
        self.assertEqual(pilha.desempilhar(), "c")

    def test_arvore_em_ordem_e_prefixo(self):
        arvore = ArvoreBST()
        for i, nome in enumerate(["Feijão", "Arroz", "Leite", "Açúcar", "Fralda"], 1):
            arvore.inserir(nome, i)
        self.assertEqual(arvore.em_ordem(), [2, 4, 1, 5, 3])
        self.assertEqual(sorted(arvore.buscar_prefixo("f")), [1, 5])
        self.assertEqual(arvore.buscar("LEITE"), [3])
        self.assertEqual(arvore.buscar("Café"), [])

    def test_merge_sort_e_busca_binaria(self):
        dados = [5, 3, 9, 1, 7]
        self.assertEqual(merge_sort(dados), [1, 3, 5, 7, 9])
        self.assertEqual(merge_sort(dados, decrescente=True), [9, 7, 5, 3, 1])
        self.assertEqual(busca_binaria([1, 3, 5, 7, 9], 7), 7)
        self.assertIsNone(busca_binaria([1, 3, 5, 7, 9], 4))


class TesteSeguranca(unittest.TestCase):
    def setUp(self):
        self.base = criar_base_demo()

    def test_senha_nao_fica_em_texto_puro(self):
        admin = self.base["usuarios"][0]
        self.assertNotIn("admin123", str(admin))

    def test_bloqueio_apos_tres_tentativas(self):
        for _ in range(3):
            usuario, _ = seguranca.autenticar(self.base, "marina", "errada1")
            self.assertIsNone(usuario)
        usuario, msg = seguranca.autenticar(self.base, "marina", "vol2025")
        self.assertIsNone(usuario)
        self.assertIn("bloqueado", msg)

    def test_recuperacao_de_senha(self):
        ok, _ = seguranca.redefinir_senha(self.base, "admin", "COMPARTILHA ", "nova123")
        self.assertTrue(ok)
        usuario, _ = seguranca.autenticar(self.base, "admin", "nova123")
        self.assertIsNotNone(usuario)


class TesteRegrasDeNegocio(unittest.TestCase):
    def setUp(self):
        self.base = criar_base_demo()
        self.admin = self.base["usuarios"][0]

    def test_nao_aceita_produto_vencido(self):
        with self.assertRaises(RegraNegocioErro):
            srv.registrar_doacao(self.base, self.admin, 1, "Macarrão", "Alimentos",
                                 5, "pct", 2, date.today() - timedelta(days=1), "")

    def test_alimento_exige_validade(self):
        with self.assertRaises(RegraNegocioErro):
            srv.registrar_doacao(self.base, self.admin, 1, "Macarrão", "Alimentos",
                                 5, "pct", 2, None, "")

    def test_vencido_fora_do_catalogo_e_no_alerta(self):
        self.assertNotIn("Biscoito Recheado", srv.catalogo_disponivel(self.base))
        vencidos = [p for p, d in srv.alertas_validade(self.base) if d < 0]
        self.assertEqual(vencidos[0]["nome"], "Biscoito Recheado")

    def test_descarte_registra_movimentacao(self):
        descartados = srv.descartar_vencidos(self.base, self.admin)
        self.assertEqual(len(descartados), 1)
        self.assertEqual(self.base["movimentacoes"][-1]["tipo"], "descarte")

    def test_fila_obriga_ordem_de_chegada(self):
        fila = srv.fila_pendentes(self.base).itens()
        with self.assertRaises(RegraNegocioErro):
            srv.avaliar_solicitacao(self.base, fila[1], True, self.admin)

    def test_aprovacao_baixa_primeiro_o_lote_que_vence_antes(self):
        primeiro = srv.fila_pendentes(self.base).primeiro()  # Arroz
        srv.avaliar_solicitacao(self.base, primeiro, True, self.admin)
        segundo = srv.fila_pendentes(self.base).primeiro()   # Feijão
        pedido = srv.por_id(self.base, "solicitacoes", segundo)["quantidade"]
        lotes = srv.lotes_para_saida(self.base, "Feijão 1kg")
        lote_que_vence_antes, lote_que_vence_depois = lotes[0], lotes[1]
        saldo_antes = lote_que_vence_antes["quantidade"]
        saldo_depois = lote_que_vence_depois["quantidade"]
        srv.avaliar_solicitacao(self.base, segundo, True, self.admin)
        self.assertEqual(lote_que_vence_antes["quantidade"], saldo_antes - pedido)
        self.assertEqual(lote_que_vence_depois["quantidade"], saldo_depois)

    def test_reprovacao_exige_motivo(self):
        primeiro = srv.fila_pendentes(self.base).primeiro()
        with self.assertRaises(RegraNegocioErro):
            srv.avaliar_solicitacao(self.base, primeiro, False, self.admin, "")

    def test_solicitacao_pendente_duplicada(self):
        with self.assertRaises(RegraNegocioErro):
            srv.criar_solicitacao(self.base, 6, "Arroz 5kg", 1, self.admin)

    def test_indicadores(self):
        ind = srv.indicadores(self.base)
        self.assertEqual(ind["em_estoque"], ind["entradas"] - ind["saidas"]
                         - ind["descartes"])
        self.assertAlmostEqual(ind["taxa_aprovacao"], 80.0)
        self.assertEqual(ind["pendentes"], 3)

    def test_relatorio_mais_solicitados_ordenado(self):
        inicio, fim = date.today() - timedelta(days=60), date.today()
        ranking = srv.relatorio_mais_solicitados(self.base, inicio, fim)
        pedidos = [r[1] for r in ranking]
        self.assertEqual(pedidos, sorted(pedidos, reverse=True))

    def test_desfazer_doacao(self):
        produto, _ = srv.registrar_doacao(self.base, self.admin, 1, "Macarrão",
                                          "Alimentos", 5, "pct", 2,
                                          date.today() + timedelta(days=60), "")
        srv.desfazer_doacao(self.base, produto["id"])
        self.assertIsNone(srv.por_id(self.base, "produtos", produto["id"]))


if __name__ == "__main__":
    unittest.main()
