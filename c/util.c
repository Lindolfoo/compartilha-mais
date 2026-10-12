/*
 * util.c
 * Implementação das funções de apoio.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include "util.h"

/* Comando de limpeza de tela conforme o sistema operacional */
#ifdef _WIN32
#define COMANDO_LIMPAR "cls"
#else
#define COMANDO_LIMPAR "clear"
#endif

void iniciarConsole(void) {
#ifdef _WIN32
    system("chcp 65001 > nul");  /* habilita UTF-8 no console do Windows */
#endif
}

void limparTela(void) {
    system(COMANDO_LIMPAR);
}

void pausar(void) {
    char lixo[8];
    printf("\nPressione ENTER para continuar...");
    fgets(lixo, sizeof(lixo), stdin);
}

void cabecalho(const char *titulo) {
    char hoje[11];
    formatarData(dataHoje(), hoje);
    limparTela();
    printf("==================================================================\n");
    printf("     COMPARTILHA+ (versão C) | Gestão de Produtos Colaborativos\n");
    printf("==================================================================\n");
    printf(">> ");
    imprimirColuna(titulo, 50);
    printf("%s\n\n", hoje);
}

void mensagemErro(const char *texto) {
    printf("[ERRO] %s\n", texto);
}

void mensagemOk(const char *texto) {
    printf("[OK] %s\n", texto);
}

/* Lê uma linha inteira com fgets (mais seguro que scanf) e remove o '\n' */
void lerTexto(const char *rotulo, char *destino, int tamanho) {
    printf("%s: ", rotulo);
    if (fgets(destino, tamanho, stdin) == NULL) {
        destino[0] = '\0';
        return;
    }
    destino[strcspn(destino, "\n")] = '\0';
}

int lerInteiro(const char *rotulo, int minimo, int maximo) {
    char linha[32];
    char *fim;
    long valor;
    while (1) {
        lerTexto(rotulo, linha, sizeof(linha));
        valor = strtol(linha, &fim, 10);
        if (fim != linha && *fim == '\0' && valor >= minimo && valor <= maximo) {
            return (int) valor;
        }
        printf("[ERRO] Digite um número entre %d e %d.\n", minimo, maximo);
    }
}

int lerConfirmacao(const char *pergunta) {
    char resposta[8];
    printf("%s (S/N): ", pergunta);
    fgets(resposta, sizeof(resposta), stdin);
    return toupper((unsigned char) resposta[0]) == 'S';
}

Data lerData(const char *rotulo, int permitirVazio) {
    char linha[32];
    Data d;
    while (1) {
        printf("%s (DD/MM/AAAA%s): ", rotulo, permitirVazio ? ", ENTER = sem data" : "");
        fgets(linha, sizeof(linha), stdin);
        linha[strcspn(linha, "\n")] = '\0';
        if (permitirVazio && linha[0] == '\0') {
            d.dia = d.mes = d.ano = 0;
            return d;
        }
        if (sscanf(linha, "%d/%d/%d", &d.dia, &d.mes, &d.ano) == 3 && dataValida(d)) {
            return d;
        }
        mensagemErro("Data inválida.");
    }
}

Data dataHoje(void) {
    time_t agora = time(NULL);
    struct tm *t = localtime(&agora);
    Data d;
    d.dia = t->tm_mday;
    d.mes = t->tm_mon + 1;
    d.ano = t->tm_year + 1900;
    return d;
}

static int bissexto(int ano) {
    return (ano % 4 == 0 && ano % 100 != 0) || ano % 400 == 0;
}

int dataValida(Data d) {
    int diasNoMes[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (d.ano < 1900 || d.ano > 2100 || d.mes < 1 || d.mes > 12) {
        return 0;
    }
    if (bissexto(d.ano)) {
        diasNoMes[1] = 29;
    }
    return d.dia >= 1 && d.dia <= diasNoMes[d.mes - 1];
}

/* Converte para time_t (meio-dia evita problemas com horário de verão) */
static time_t paraTimeT(Data d) {
    struct tm t;
    memset(&t, 0, sizeof(t));
    t.tm_mday = d.dia;
    t.tm_mon = d.mes - 1;
    t.tm_year = d.ano - 1900;
    t.tm_hour = 12;
    return mktime(&t);
}

int diasAte(Data d) {
    double segundos = difftime(paraTimeT(d), paraTimeT(dataHoje()));
    return (int) (segundos / 86400.0 + (segundos >= 0 ? 0.5 : -0.5));
}

void formatarData(Data d, char *destino) {
    if (d.ano == 0) {
        strcpy(destino, "-");
    } else {
        sprintf(destino, "%02d/%02d/%04d", d.dia, d.mes, d.ano);
    }
}

int contemIgnorandoCaixa(const char *texto, const char *trecho) {
    char a[100], b[100];
    int i;
    for (i = 0; texto[i] && i < 99; i++) a[i] = (char) tolower((unsigned char) texto[i]);
    a[i] = '\0';
    for (i = 0; trecho[i] && i < 99; i++) b[i] = (char) tolower((unsigned char) trecho[i]);
    b[i] = '\0';
    return strstr(a, b) != NULL;
}

/*
 * Imprime o texto ocupando exatamente 'largura' caracteres visíveis.
 * Necessária porque, em UTF-8, letras acentuadas ocupam 2 bytes e o
 * printf("%-20s") conta bytes, desalinhando as tabelas.
 */
void imprimirColuna(const char *texto, int largura) {
    int i = 0, visiveis = 0;
    while (texto[i] != '\0') {
        /* bytes 10xxxxxx são continuação de um caractere UTF-8 */
        if (((unsigned char) texto[i] & 0xC0) != 0x80) {
            if (visiveis == largura) {
                break;
            }
            visiveis++;
        }
        putchar(texto[i]);
        i++;
    }
    while (visiveis < largura) {
        putchar(' ');
        visiveis++;
    }
    putchar(' ');
}
