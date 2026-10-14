/*
 * estoque.c
 * Cadastro de produtos, movimentações de estoque, controle de validade e
 * relatório, com gravação dos dados em arquivos binários.
 */
#include <stdio.h>
#include <string.h>
#include "estoque.h"

Produto   produtos[MAX_PRODUTOS];
int       totalProdutos = 0;
Movimento movimentos[MAX_MOVIMENTOS];
int       totalMovimentos = 0;

static const char *CATEGORIAS[] = {
    "Alimentos", "Higiene", "Medicamentos", "Brinquedos", "Vestuário", "Outros"
};
#define TOTAL_CATEGORIAS 6

/* ------------------------------------------------------------------ */
/* ARQUIVOS                                                            */
/* ------------------------------------------------------------------ */
void carregarDados(void) {
    FILE *arq = fopen(ARQ_PRODUTOS, "rb");
    if (arq != NULL) {
        totalProdutos = (int) fread(produtos, sizeof(Produto), MAX_PRODUTOS, arq);
        fclose(arq);
    }
    arq = fopen(ARQ_MOVIMENTOS, "rb");
    if (arq != NULL) {
        totalMovimentos = (int) fread(movimentos, sizeof(Movimento), MAX_MOVIMENTOS, arq);
        fclose(arq);
    }
}

void salvarDados(void) {
    FILE *arq = fopen(ARQ_PRODUTOS, "wb");
    if (arq == NULL) {
        mensagemErro("Não foi possível gravar o arquivo de produtos.");
        return;
    }
    fwrite(produtos, sizeof(Produto), (size_t) totalProdutos, arq);
    fclose(arq);

    arq = fopen(ARQ_MOVIMENTOS, "wb");
    if (arq == NULL) {
        mensagemErro("Não foi possível gravar o arquivo de movimentações.");
        return;
    }
    fwrite(movimentos, sizeof(Movimento), (size_t) totalMovimentos, arq);
    fclose(arq);
}

/* ------------------------------------------------------------------ */
/* AUXILIARES                                                          */
/* ------------------------------------------------------------------ */
Produto *buscarPorCodigo(int codigo) {
    int i;
    for (i = 0; i < totalProdutos; i++) {
        if (produtos[i].codigo == codigo) {
            return &produtos[i];
        }
    }
    return NULL;
}

/* Ordenação por inserção usando ponteiros (não move os registros) */
void ordenarPorNome(Produto *lista[], int n) {
    int i, j;
    Produto *atual;
    for (i = 1; i < n; i++) {
        atual = lista[i];
        j = i - 1;
        while (j >= 0 && strcmp(lista[j]->nome, atual->nome) > 0) {
            lista[j + 1] = lista[j];
            j--;
        }
        lista[j + 1] = atual;
    }
}

static int vencido(const Produto *p) {
    return p->validade.ano != 0 && diasAte(p->validade) < 0;
}

static void registrarMovimento(int codigoProduto, char tipo, int quantidade,
                               const char *observacao) {
    Movimento *m;
    if (totalMovimentos >= MAX_MOVIMENTOS) {
        mensagemErro("Limite de movimentações atingido.");
        return;
    }
    m = &movimentos[totalMovimentos];
    m->codigo = totalMovimentos + 1;
    m->codigoProduto = codigoProduto;
    m->tipo = tipo;
    m->quantidade = quantidade;
    m->data = dataHoje();
    strncpy(m->observacao, observacao, sizeof(m->observacao) - 1);
    m->observacao[sizeof(m->observacao) - 1] = '\0';
    totalMovimentos++;
}

static void imprimirCabecalhoTabela(void) {
    imprimirColuna("Cód", 5);
    imprimirColuna("Produto", 24);
    imprimirColuna("Categoria", 13);
    printf("%8s %-6s %-11s %s\n", "Saldo", "Un", "Validade", "Situação");
    printf("------------------------------------------------------------------------------\n");
}

static void imprimirProduto(const Produto *p) {
    char validade[11], situacao[20];
    formatarData(p->validade, validade);
    if (!p->ativo) {
        strcpy(situacao, "descartado");
    } else if (p->validade.ano == 0) {
        strcpy(situacao, "-");
    } else if (vencido(p)) {
        strcpy(situacao, "VENCIDO");
    } else {
        sprintf(situacao, "vence em %d d", diasAte(p->validade));
    }
    printf("%-5d ", p->codigo);
    imprimirColuna(p->nome, 24);
    imprimirColuna(p->categoria, 13);
    printf("%8d %-6.6s %-11s %s\n", p->quantidade, p->unidade, validade, situacao);
}

/* ------------------------------------------------------------------ */
/* TELAS DE PRODUTOS                                                   */
/* ------------------------------------------------------------------ */
void telaCadastrarProduto(void) {
    Produto novo;
    int i, opcao;

    cabecalho("CADASTRO DE PRODUTO");
    if (totalProdutos >= MAX_PRODUTOS) {
        mensagemErro("Limite de produtos atingido.");
        pausar();
        return;
    }
    memset(&novo, 0, sizeof(novo));
    novo.codigo = totalProdutos + 1;

    lerTexto("Nome do produto", novo.nome, sizeof(novo.nome));
    while (strlen(novo.nome) < 2) {
        mensagemErro("Informe o nome do produto.");
        lerTexto("Nome do produto", novo.nome, sizeof(novo.nome));
    }
    for (i = 0; i < TOTAL_CATEGORIAS; i++) {
        printf("  %d - %s\n", i + 1, CATEGORIAS[i]);
    }
    opcao = lerInteiro("Categoria", 1, TOTAL_CATEGORIAS);
    strcpy(novo.categoria, CATEGORIAS[opcao - 1]);
    lerTexto("Doador", novo.doador, sizeof(novo.doador));
    novo.quantidade = lerInteiro("Quantidade", 1, 100000);
    lerTexto("Unidade (un, pct, cx...)", novo.unidade, sizeof(novo.unidade));

    /* Alimentos, higiene e medicamentos exigem validade (opções 1 a 3) */
    while (1) {
        novo.validade = lerData("Validade", opcao > 3);
        if (novo.validade.ano != 0 && diasAte(novo.validade) < 0) {
            mensagemErro("Não é permitido receber produto vencido.");
        } else {
            break;
        }
    }
    lerTexto("Lote", novo.lote, sizeof(novo.lote));
    novo.ativo = 1;

    produtos[totalProdutos++] = novo;
    registrarMovimento(novo.codigo, 'E', novo.quantidade, "Doação inicial");
    salvarDados();
    printf("\n");
    mensagemOk("Produto cadastrado com sucesso.");
    printf("Código gerado: %d\n", novo.codigo);
    pausar();
}

void telaListarProdutos(void) {
    Produto *lista[MAX_PRODUTOS];
    int i, n = 0;

    cabecalho("ESTOQUE EM ORDEM ALFABÉTICA");
    for (i = 0; i < totalProdutos; i++) {
        if (produtos[i].ativo) {
            lista[n++] = &produtos[i];
        }
    }
    if (n == 0) {
        printf("Nenhum produto em estoque.\n");
        pausar();
        return;
    }
    ordenarPorNome(lista, n);
    imprimirCabecalhoTabela();
    for (i = 0; i < n; i++) {
        imprimirProduto(lista[i]);
    }
    printf("\nTotal de produtos: %d\n", n);
    pausar();
}

void telaBuscarProduto(void) {
    char termo[50];
    int i, encontrados = 0;

    cabecalho("BUSCA DE PRODUTO");
    lerTexto("Digite parte do nome", termo, sizeof(termo));
    printf("\n");
    imprimirCabecalhoTabela();
    for (i = 0; i < totalProdutos; i++) {
        if (contemIgnorandoCaixa(produtos[i].nome, termo)) {
            imprimirProduto(&produtos[i]);
            encontrados++;
        }
    }
    printf("\n%d produto(s) encontrado(s).\n", encontrados);
    pausar();
}

/* ------------------------------------------------------------------ */
/* TELAS DE MOVIMENTAÇÃO                                               */
/* ------------------------------------------------------------------ */
static Produto *escolherProduto(void) {
    Produto *p;
    int codigo = lerInteiro("Código do produto", 1, 100000);
    p = buscarPorCodigo(codigo);
    if (p == NULL || !p->ativo) {
        mensagemErro("Produto não encontrado.");
        return NULL;
    }
    imprimirCabecalhoTabela();
    imprimirProduto(p);
    printf("\n");
    return p;
}

void telaEntrada(void) {
    Produto *p;
    int qtd;
    char obs[60];

    cabecalho("ENTRADA DE PRODUTO (NOVA DOAÇÃO)");
    p = escolherProduto();
    if (p != NULL) {
        qtd = lerInteiro("Quantidade recebida", 1, 100000);
        lerTexto("Observação (doador)", obs, sizeof(obs));
        p->quantidade += qtd;
        registrarMovimento(p->codigo, 'E', qtd, obs);
        salvarDados();
        mensagemOk("Entrada registrada.");
        printf("Novo saldo: %d %s\n", p->quantidade, p->unidade);
    }
    pausar();
}

void telaSaida(void) {
    Produto *p;
    int qtd;
    char obs[60];

    cabecalho("SAÍDA DE PRODUTO (ENTREGA)");
    p = escolherProduto();
    if (p != NULL) {
        if (vencido(p)) {
            mensagemErro("Produto vencido não pode ser entregue. Faça o descarte.");
        } else if (p->quantidade == 0) {
            mensagemErro("Produto sem saldo.");
        } else {
            qtd = lerInteiro("Quantidade entregue", 1, p->quantidade);
            lerTexto("Observação (solicitante)", obs, sizeof(obs));
            p->quantidade -= qtd;
            registrarMovimento(p->codigo, 'S', qtd, obs);
            salvarDados();
            mensagemOk("Saída registrada.");
            printf("Novo saldo: %d %s\n", p->quantidade, p->unidade);
        }
    }
    pausar();
}

void telaHistorico(void) {
    int i;
    char data[11];
    Produto *p;
    const char *tipo;

    cabecalho("HISTÓRICO DE MOVIMENTAÇÕES");
    if (totalMovimentos == 0) {
        printf("Nenhuma movimentação registrada.\n");
        pausar();
        return;
    }
    imprimirColuna("Nº", 5);
    printf("%-11s %-9s %-22s %6s  %s\n", "Data", "Tipo", "Produto", "Qtd", "Observação");
    printf("------------------------------------------------------------------------------\n");
    for (i = totalMovimentos - 1; i >= 0; i--) {  /* mais recente primeiro */
        p = buscarPorCodigo(movimentos[i].codigoProduto);
        formatarData(movimentos[i].data, data);
        tipo = movimentos[i].tipo == 'E' ? "Entrada" :
               movimentos[i].tipo == 'S' ? "Saída" : "Descarte";
        printf("%-5d %-11s ", movimentos[i].codigo, data);
        imprimirColuna(tipo, 9);
        imprimirColuna(p ? p->nome : "?", 22);
        printf("%6d  %.25s\n", movimentos[i].quantidade, movimentos[i].observacao);
    }
    pausar();
}

/* ------------------------------------------------------------------ */
/* VALIDADE                                                            */
/* ------------------------------------------------------------------ */
void telaAlertasValidade(void) {
    int i, alertas = 0;

    cabecalho("ALERTAS DE VALIDADE");
    printf("Produtos vencidos ou que vencem em até %d dias:\n\n", DIAS_ALERTA);
    imprimirCabecalhoTabela();
    for (i = 0; i < totalProdutos; i++) {
        Produto *p = &produtos[i];
        if (p->ativo && p->quantidade > 0 && p->validade.ano != 0 &&
            diasAte(p->validade) <= DIAS_ALERTA) {
            imprimirProduto(p);
            alertas++;
        }
    }
    printf("\n%d produto(s) em alerta.\n", alertas);
    pausar();
}

void telaDescartarVencidos(void) {
    int i, total = 0;

    cabecalho("DESCARTE DE PRODUTOS VENCIDOS");
    imprimirCabecalhoTabela();
    for (i = 0; i < totalProdutos; i++) {
        if (produtos[i].ativo && produtos[i].quantidade > 0 && vencido(&produtos[i])) {
            imprimirProduto(&produtos[i]);
            total++;
        }
    }
    if (total == 0) {
        printf("\nNão há produtos vencidos.\n");
        pausar();
        return;
    }
    if (lerConfirmacao("\nConfirmar o descarte dos produtos listados?")) {
        for (i = 0; i < totalProdutos; i++) {
            if (produtos[i].ativo && produtos[i].quantidade > 0 && vencido(&produtos[i])) {
                registrarMovimento(produtos[i].codigo, 'D', produtos[i].quantidade,
                                   "Descarte por vencimento");
                produtos[i].quantidade = 0;
                produtos[i].ativo = 0;
            }
        }
        salvarDados();
        mensagemOk("Descarte registrado. Encaminhe os itens a um ponto de coleta.");
    }
    pausar();
}

/* ------------------------------------------------------------------ */
/* RELATÓRIO                                                           */
/* ------------------------------------------------------------------ */
void telaRelatorio(void) {
    int entradas = 0, saidas = 0, descartes = 0, i, c;
    int saldoCategoria[TOTAL_CATEGORIAS] = {0};

    cabecalho("RELATÓRIO GERAL");
    for (i = 0; i < totalMovimentos; i++) {
        if (movimentos[i].tipo == 'E') entradas += movimentos[i].quantidade;
        else if (movimentos[i].tipo == 'S') saidas += movimentos[i].quantidade;
        else descartes += movimentos[i].quantidade;
    }
    for (i = 0; i < totalProdutos; i++) {
        for (c = 0; c < TOTAL_CATEGORIAS; c++) {
            if (strcmp(produtos[i].categoria, CATEGORIAS[c]) == 0) {
                saldoCategoria[c] += produtos[i].quantidade;
            }
        }
    }
    printf("Unidades recebidas ........ %d\n", entradas);
    printf("Unidades entregues ........ %d\n", saidas);
    printf("Unidades descartadas ...... %d\n", descartes);
    printf("Saldo atual ............... %d\n", entradas - saidas - descartes);
    if (entradas > 0) {
        printf("Aproveitamento ............ %.1f%%\n", saidas * 100.0 / entradas);
        printf("Perda por vencimento ...... %.1f%%\n", descartes * 100.0 / entradas);
    }
    printf("\nSaldo por categoria:\n");
    for (c = 0; c < TOTAL_CATEGORIAS; c++) {
        printf("  ");
        imprimirColuna(CATEGORIAS[c], 14);
        printf("%6d\n", saldoCategoria[c]);
    }
    pausar();
}
