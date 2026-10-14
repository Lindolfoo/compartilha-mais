/*
 * estoque.h
 * Estruturas e protótipos do controle de produtos e movimentações.
 */
#ifndef ESTOQUE_H
#define ESTOQUE_H

#include "util.h"

#define MAX_PRODUTOS     500
#define MAX_MOVIMENTOS   2000
#define DIAS_ALERTA      30
#define ARQ_PRODUTOS     "produtos.dat"
#define ARQ_MOVIMENTOS   "movimentos.dat"

typedef struct {
    int  codigo;
    char nome[50];
    char categoria[20];
    char doador[50];
    int  quantidade;
    char unidade[10];
    Data validade;      /* ano = 0 quando o produto não tem validade */
    char lote[15];
    int  ativo;         /* 0 = descartado */
} Produto;

typedef struct {
    int  codigo;
    int  codigoProduto;
    char tipo;          /* 'E' = entrada, 'S' = saída, 'D' = descarte */
    int  quantidade;
    Data data;
    char observacao[60];
} Movimento;

/* Vetores globais (definidos em estoque.c) */
extern Produto   produtos[MAX_PRODUTOS];
extern int       totalProdutos;
extern Movimento movimentos[MAX_MOVIMENTOS];
extern int       totalMovimentos;

/* Arquivos */
void carregarDados(void);
void salvarDados(void);

/* Telas */
void telaCadastrarProduto(void);
void telaListarProdutos(void);
void telaBuscarProduto(void);
void telaEntrada(void);
void telaSaida(void);
void telaHistorico(void);
void telaAlertasValidade(void);
void telaDescartarVencidos(void);
void telaRelatorio(void);

/* Auxiliares */
Produto *buscarPorCodigo(int codigo);
void ordenarPorNome(Produto *lista[], int n);

#endif
