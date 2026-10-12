# Compartilha+ — versão em C

Versão complementar, em linguagem C (padrão C99), com cadastro de produtos,
entradas e saídas de estoque, controle de validade e relatório geral.
Os dados são gravados em arquivos binários (`produtos.dat` e `movimentos.dat`).

## Compilar e executar
```bash
gcc -std=c99 -Wall main.c util.c estoque.c -o compartilha
./compartilha            # Linux/macOS
compartilha.exe          # Windows
```
Ou, com o `make` instalado: `make`.

Acesso: usuário `admin`, senha `admin123` (3 tentativas).

## Arquivos
| Arquivo     | Conteúdo                                                        |
|-------------|-----------------------------------------------------------------|
| `main.c`    | Função `main`, login e menus (Produtos, Movimentações, Validade) |
| `estoque.h` | Estruturas `Produto` e `Movimento` e protótipos                 |
| `estoque.c` | Cadastro, listagem ordenada, busca, entradas/saídas, validade, relatório e arquivos |
| `util.h/.c` | Limpeza de tela, leitura validada, datas com `time.h`, alinhamento UTF-8 |
