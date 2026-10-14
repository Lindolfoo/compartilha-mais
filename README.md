# Compartilha+ — Sistema para Gestão de Produtos Colaborativos

Projeto Integrado Multidisciplinar II (PIM II) — CST em Análise e Desenvolvimento
de Sistemas, Universidade Paulista (UNIP), Sorocaba, 2026.

Sistema para iniciativas de doação de alimentos, produtos de higiene,
medicamentos, brinquedos e roupas. Substitui o controle em papel por um processo
rastreável: cada lote tem origem, validade e destino registrados, os pedidos são
atendidos em uma fila por ordem de chegada e a baixa do estoque consome primeiro
o lote que vence antes (PVPS).

## Funcionalidades

- **Acesso:** três perfis (administrador, voluntário, solicitante), senhas com hash
  PBKDF2, bloqueio após três tentativas e recuperação por pergunta de segurança.
- **Cadastros:** doadores e solicitantes (CPF/CNPJ), funcionários e voluntários.
- **Estoque:** registro de doações por lote, listagem em ordem alfabética, busca
  com filtros, alertas de validade (até 30 dias) e descarte de vencidos.
- **Solicitações:** fila por ordem de chegada, aprovação ou reprovação com motivo
  e baixa automática pelo critério PVPS.
- **Relatórios:** entradas e saídas, mais solicitados, doações por doador e por
  mês, indicadores de aproveitamento, perda, aprovação e tempo de espera.
- **Sistema:** gravação atômica em JSON, backup automático com rotação e
  restauração, desfazer a última doação.

## Estrutura do repositório

| Pasta | Conteúdo |
|-------|----------|
| [`python/`](python/) | Sistema completo em Python 3 (somente biblioteca padrão) |
| [`c/`](c/) | Versão complementar em C99: estoque, validade e arquivos binários |
| [`docs/`](docs/) | Requisitos, artefatos do Scrum e diagramas (fontes PlantUML e imagens) |
| [`.github/`](.github/) | Modelos de issue e pull request e testes automáticos (GitHub Actions) |

## Como executar

**Python** (3.8 ou superior):

```bash
cd python
python main.py --demo      # cria uma base de demonstração e inicia o sistema
```

| Perfil | Login | Senha |
|--------|-------|-------|
| Administrador | `admin` | `admin123` |
| Voluntário | `marina` | `vol2025` |
| Solicitante | `ana` | `ana2025` |

**C** (GCC, padrão C99):

```bash
cd c
make                       # ou: gcc -std=c99 -Wall -Wextra -pedantic main.c util.c estoque.c -o compartilha
./compartilha              # login: admin / admin123
```

## Testes

```bash
cd python
python -m unittest discover -s testes -v     # 18 testes automatizados
```

Os testes rodam no GitHub Actions a cada pull request, em Linux e Windows, junto
com a compilação da versão em C sem nenhum aviso.

## Processo de desenvolvimento

O projeto foi conduzido com Scrum em seis Sprints semanais
([backlog, Sprints e definição de pronto](docs/scrum/README.md)).

- Cada item do Product Backlog é uma *issue*; cada Sprint, um *milestone*.
- Cada funcionalidade é desenvolvida em uma branch `feature/<nome>` e integrada à
  `main` por *pull request* revisado ([como contribuir](CONTRIBUTING.md)).
- Commits no padrão `tipo: descrição` (`feat`, `fix`, `test`, `docs`, `chore`).
- A versão entregue é marcada com a tag `v1.0`.

## Equipe

| Integrante | Papel no Scrum |
|------------|----------------|
| Ricardo de Almeida Costa | Product Owner |
| Caio Silva dos Santos | Scrum Master |
| Andrey Rodrigues de Carvalho Silva | Developer |
| Henrique Rodrigues Lindolfo | Developer |

Orientador: Prof. Me. Waldir Silva.
