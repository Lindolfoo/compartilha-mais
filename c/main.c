/*
 * main.c
 * Compartilha+ (versão em C) - ponto de entrada, login e menus.
 *
 * Compilar:  gcc main.c util.c estoque.c -o compartilha
 * Executar:  ./compartilha   (Windows: compartilha.exe)
 */
#include <stdio.h>
#include <string.h>
#include "util.h"
#include "estoque.h"

#define MAX_TENTATIVAS 3
#define USUARIO_PADRAO "admin"
#define SENHA_PADRAO   "admin123"

static int telaLogin(void);
static void menuProdutos(void);
static void menuMovimentacoes(void);
static void menuValidade(void);

int main(void) {
    int opcao;

    iniciarConsole();
    carregarDados();

    if (!telaLogin()) {
        printf("\nAcesso bloqueado após %d tentativas. Encerrando.\n", MAX_TENTATIVAS);
        return 1;
    }

    do {
        cabecalho("MENU PRINCIPAL");
        printf("  1 - Produtos\n");
        printf("  2 - Movimentações (entradas e saídas)\n");
        printf("  3 - Controle de validade\n");
        printf("  4 - Relatório geral\n");
        printf("  0 - Sair\n\n");
        opcao = lerInteiro("Escolha uma opção", 0, 4);

        switch (opcao) {
            case 1: menuProdutos();      break;
            case 2: menuMovimentacoes(); break;
            case 3: menuValidade();      break;
            case 4: telaRelatorio();     break;
            case 0: printf("\nDados salvos. Encerrando o sistema...\n"); break;
        }
    } while (opcao != 0);

    salvarDados();
    return 0;
}

/* Login com limite de tentativas */
static int telaLogin(void) {
    char usuario[30], senha[30];
    int tentativa;

    for (tentativa = 1; tentativa <= MAX_TENTATIVAS; tentativa++) {
        cabecalho("ACESSO AO SISTEMA");
        lerTexto("Usuário", usuario, sizeof(usuario));
        lerTexto("Senha", senha, sizeof(senha));
        if (strcmp(usuario, USUARIO_PADRAO) == 0 && strcmp(senha, SENHA_PADRAO) == 0) {
            mensagemOk("Acesso liberado.");
            pausar();
            return 1;
        }
        printf("[ERRO] Usuário ou senha incorretos. Tentativas restantes: %d\n",
               MAX_TENTATIVAS - tentativa);
        pausar();
    }
    return 0;
}

static void menuProdutos(void) {
    int opcao;
    do {
        cabecalho("PRODUTOS");
        printf("  1 - Cadastrar produto (doação)\n");
        printf("  2 - Listar estoque em ordem alfabética\n");
        printf("  3 - Buscar produto por nome\n");
        printf("  0 - Voltar\n\n");
        opcao = lerInteiro("Escolha uma opção", 0, 3);
        switch (opcao) {
            case 1: telaCadastrarProduto(); break;
            case 2: telaListarProdutos();   break;
            case 3: telaBuscarProduto();    break;
        }
    } while (opcao != 0);
}

static void menuMovimentacoes(void) {
    int opcao;
    do {
        cabecalho("MOVIMENTAÇÕES");
        printf("  1 - Registrar entrada (nova doação de produto existente)\n");
        printf("  2 - Registrar saída (entrega a solicitante)\n");
        printf("  3 - Histórico de movimentações\n");
        printf("  0 - Voltar\n\n");
        opcao = lerInteiro("Escolha uma opção", 0, 3);
        switch (opcao) {
            case 1: telaEntrada();   break;
            case 2: telaSaida();     break;
            case 3: telaHistorico(); break;
        }
    } while (opcao != 0);
}

static void menuValidade(void) {
    int opcao;
    do {
        cabecalho("CONTROLE DE VALIDADE");
        printf("  1 - Alertas de validade\n");
        printf("  2 - Descartar produtos vencidos\n");
        printf("  0 - Voltar\n\n");
        opcao = lerInteiro("Escolha uma opção", 0, 2);
        switch (opcao) {
            case 1: telaAlertasValidade();   break;
            case 2: telaDescartarVencidos(); break;
        }
    } while (opcao != 0);
}
