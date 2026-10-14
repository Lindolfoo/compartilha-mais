/*
 * util.h
 * Funções de apoio: tela, leitura validada de dados e datas (time.h).
 */
#ifndef UTIL_H
#define UTIL_H

/* Data simples. Para produtos sem validade usa-se ano = 0. */
typedef struct {
    int dia;
    int mes;
    int ano;
} Data;

void iniciarConsole(void);
void limparTela(void);
void pausar(void);
void cabecalho(const char *titulo);
void mensagemErro(const char *texto);
void mensagemOk(const char *texto);

void lerTexto(const char *rotulo, char *destino, int tamanho);
int  lerInteiro(const char *rotulo, int minimo, int maximo);
int  lerConfirmacao(const char *pergunta);
Data lerData(const char *rotulo, int permitirVazio);

Data dataHoje(void);
int  dataValida(Data d);
int  diasAte(Data d);              /* dias entre hoje e a data (negativo = passou) */
void formatarData(Data d, char *destino);
int  contemIgnorandoCaixa(const char *texto, const char *trecho);
void imprimirColuna(const char *texto, int largura);

#endif
