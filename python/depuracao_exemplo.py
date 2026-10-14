"""
depuracao_exemplo.py
Cenário usado na depuração passo a passo (pdb) da baixa de estoque.
Uma solicitação de 50 pacotes de feijão precisa consumir dois lotes:
primeiro o que vence antes (critério PVPS) e depois o seguinte.

Executar:  python -m pdb depuracao_exemplo.py
"""
import servicos as srv
from demo import criar_base_demo

base = criar_base_demo()
admin = base["usuarios"][0]

# Esvazia a fila para que a nova solicitação seja a primeira
for sid in srv.fila_pendentes(base).itens():
    srv.avaliar_solicitacao(base, sid, False, admin, "Cenário de teste")

pedido = srv.criar_solicitacao(base, 6, "Feijão 1kg", 50, admin)
srv.avaliar_solicitacao(base, pedido["id"], True, admin)
print("Saldo final dos lotes de feijão:",
      [(l["id"], l["quantidade"]) for l in base["produtos"] if l["nome"] == "Feijão 1kg"])
