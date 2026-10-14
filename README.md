# Compartilha+ — Gestão de Produtos Colaborativos

Projeto Integrado Multidisciplinar II — CST em Análise e Desenvolvimento de Sistemas (UNIP).

Sistema para iniciativas de doação de produtos (alimentos, higiene, medicamentos,
brinquedos e vestuário): cadastro de doadores, solicitantes e voluntários; controle
de estoque com alertas de validade; fila justa de solicitações com aprovação;
relatórios e backup automático.

| Pasta     | Conteúdo                                              |
|-----------|-------------------------------------------------------|
| `python/` | Sistema completo em Python 3 (ver `python/README.md`) |
| `c/`      | Versão complementar em C99 (ver `c/README.md`)        |
| `docs/`   | Diagramas (fontes PlantUML)                           |

## Execução rápida
```bash
cd python && python main.py --demo      # login: admin / admin123
cd c && gcc -std=c99 main.c util.c estoque.c -o compartilha && ./compartilha
```

## Fluxo de trabalho no Git
- `main`: versão estável, só recebe merges revisados.
- `feature/<nome>`: uma branch por item do Product Backlog, integrada por pull request.
- Mensagens de commit no padrão `tipo: descrição` (feat, fix, test, docs, chore).
