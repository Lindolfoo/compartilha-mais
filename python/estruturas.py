"""
estruturas.py
Estruturas de dados implementadas manualmente para o sistema Compartilha+.

- Fila  (FIFO): ordena as solicitações por ordem de chegada (acesso justo).
- Pilha (LIFO): guarda as ações da sessão para permitir desfazer a última.
- ArvoreBST   : índice de produtos por nome, com listagem em ordem alfabética
                e busca por prefixo.
- merge_sort  : ordenação estável usada nos relatórios e no critério de
                saída por validade (o que vence primeiro sai primeiro).
- busca_binaria: localização rápida de registros pelo código (id).
"""


# ----------------------------------------------------------------------
# FILA (primeiro a entrar, primeiro a sair)
# ----------------------------------------------------------------------
class Fila:
    def __init__(self):
        self._itens = []  # lista que armazena os elementos da fila

    def enfileirar(self, item):
        self._itens.append(item)  # insere no final da fila

    def desenfileirar(self):
        if self.vazia():
            return None
        return self._itens.pop(0)  # remove do início da fila

    def primeiro(self):
        return None if self.vazia() else self._itens[0]

    def remover(self, item):
        if item in self._itens:
            self._itens.remove(item)

    def vazia(self):
        return len(self._itens) == 0

    def tamanho(self):
        return len(self._itens)

    def itens(self):
        return list(self._itens)  # cópia, para não alterar a fila por fora


# ----------------------------------------------------------------------
# PILHA (último a entrar, primeiro a sair)
# ----------------------------------------------------------------------
class Pilha:
    def __init__(self, limite=20):
        self._itens = []
        self._limite = limite  # guarda apenas as últimas N ações

    def empilhar(self, item):
        self._itens.append(item)
        if len(self._itens) > self._limite:
            self._itens.pop(0)  # descarta a ação mais antiga

    def desempilhar(self):
        return self._itens.pop() if self._itens else None

    def topo(self):
        return self._itens[-1] if self._itens else None

    def vazia(self):
        return len(self._itens) == 0

    def itens(self):
        return list(reversed(self._itens))  # do mais recente ao mais antigo


# ----------------------------------------------------------------------
# ÁRVORE BINÁRIA DE BUSCA (índice de produtos por nome)
# ----------------------------------------------------------------------
class NoArvore:
    def __init__(self, chave, valor):
        self.chave = chave        # nome do produto em minúsculas
        self.valores = [valor]    # ids dos produtos com esse nome
        self.esquerda = None
        self.direita = None


class ArvoreBST:
    def __init__(self):
        self.raiz = None

    def inserir(self, chave, valor):
        chave = chave.lower().strip()
        if self.raiz is None:
            self.raiz = NoArvore(chave, valor)
            return
        atual = self.raiz
        while True:  # versão iterativa da inserção
            if chave == atual.chave:
                if valor not in atual.valores:
                    atual.valores.append(valor)
                return
            if chave < atual.chave:
                if atual.esquerda is None:
                    atual.esquerda = NoArvore(chave, valor)
                    return
                atual = atual.esquerda
            else:
                if atual.direita is None:
                    atual.direita = NoArvore(chave, valor)
                    return
                atual = atual.direita

    def buscar(self, chave):
        """Retorna a lista de ids com o nome exato, ou lista vazia."""
        chave = chave.lower().strip()
        atual = self.raiz
        while atual is not None:
            if chave == atual.chave:
                return list(atual.valores)
            atual = atual.esquerda if chave < atual.chave else atual.direita
        return []

    def em_ordem(self):
        """Percurso em ordem (recursivo): devolve os ids em ordem alfabética."""
        resultado = []
        self._em_ordem(self.raiz, resultado)
        return resultado

    def _em_ordem(self, no, resultado):
        if no is None:
            return
        self._em_ordem(no.esquerda, resultado)
        resultado.extend(no.valores)
        self._em_ordem(no.direita, resultado)

    def buscar_prefixo(self, prefixo):
        """Busca por prefixo: só visita os ramos que podem conter o prefixo."""
        prefixo = prefixo.lower().strip()
        resultado = []
        self._prefixo(self.raiz, prefixo, resultado)
        return resultado

    def _prefixo(self, no, prefixo, resultado):
        if no is None:
            return
        if no.chave.startswith(prefixo):
            # o nó combina: pode haver resultados dos dois lados
            self._prefixo(no.esquerda, prefixo, resultado)
            resultado.extend(no.valores)
            self._prefixo(no.direita, prefixo, resultado)
        elif no.chave < prefixo:
            # tudo à esquerda é menor ainda: só o lado direito interessa
            self._prefixo(no.direita, prefixo, resultado)
        else:
            # tudo à direita é maior ainda: só o lado esquerdo interessa
            self._prefixo(no.esquerda, prefixo, resultado)

    def altura(self, no="raiz"):
        if no == "raiz":
            no = self.raiz
        if no is None:
            return 0
        return 1 + max(self.altura(no.esquerda), self.altura(no.direita))


# ----------------------------------------------------------------------
# MERGE SORT (ordenação estável, O(n log n))
# ----------------------------------------------------------------------
def merge_sort(lista, chave=lambda x: x, decrescente=False):
    if len(lista) <= 1:
        return list(lista)
    meio = len(lista) // 2
    esquerda = merge_sort(lista[:meio], chave, decrescente)
    direita = merge_sort(lista[meio:], chave, decrescente)
    return _intercalar(esquerda, direita, chave, decrescente)


def _intercalar(a, b, chave, decrescente):
    resultado = []
    i = j = 0
    while i < len(a) and j < len(b):
        if decrescente:
            pega_a = chave(a[i]) >= chave(b[j])
        else:
            pega_a = chave(a[i]) <= chave(b[j])
        if pega_a:
            resultado.append(a[i])
            i += 1
        else:
            resultado.append(b[j])
            j += 1
    resultado.extend(a[i:])
    resultado.extend(b[j:])
    return resultado


# ----------------------------------------------------------------------
# BUSCA BINÁRIA (lista precisa estar ordenada pela chave)
# ----------------------------------------------------------------------
def busca_binaria(lista, alvo, chave=lambda x: x):
    inicio, fim = 0, len(lista) - 1
    while inicio <= fim:
        meio = (inicio + fim) // 2
        valor = chave(lista[meio])
        if valor == alvo:
            return lista[meio]
        if valor < alvo:
            inicio = meio + 1
        else:
            fim = meio - 1
    return None
