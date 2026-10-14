# Scrum no Compartilha+

Artefatos do processo descrito no Capítulo 3 do relatório técnico.

## Papéis

| Papel | Integrante | Responsabilidades |
|-------|------------|-------------------|
| Product Owner | Ricardo de Almeida Costa | Manter e priorizar o Product Backlog; aceitar ou recusar os incrementos na Sprint Review. |
| Scrum Master | Caio Silva dos Santos | Conduzir os eventos, remover impedimentos e zelar pela definição de pronto. |
| Developers | Andrey Rodrigues de Carvalho Silva e Henrique Rodrigues Lindolfo | Modelar, implementar, testar e documentar os itens de cada Sprint. |

Sprints de uma semana: Sprint Planning no início, acompanhamento diário curto,
Sprint Review com o incremento em execução e Sprint Retrospective ao final.

## Product Backlog

Histórias no formato "como <papel>, quero <ação> para <benefício>", estimadas em
pontos (Fibonacci). Cada linha corresponde a uma *issue* no GitHub com o mesmo
código, e cada Sprint a um *milestone*.

| ID | História de usuário | Pontos | Sprint | Requisitos |
|----|---------------------|--------|--------|------------|
| PB01 | Como usuário, quero entrar com login e senha e ver apenas as funções do meu perfil, para proteger os dados. | 8 | 2 | RF01, RF02, RNF04 |
| PB02 | Como usuário, quero recuperar minha senha por pergunta de segurança, para não perder o acesso. | 3 | 2 | RF03 |
| PB03 | Como sistema, quero gravar os dados em arquivo com backup automático, para não perder informações. | 5 | 2 | RF21, RNF05 |
| PB04 | Como voluntário, quero cadastrar doadores e solicitantes, para identificar cada movimentação. | 5 | 3 | RF05, RN09 |
| PB05 | Como administrador, quero cadastrar funcionários e voluntários, para controlar quem opera o sistema. | 3 | 3 | RF06 |
| PB06 | Como voluntário, quero registrar uma doação com validade e lote, para manter o estoque rastreável. | 5 | 3 | RF04, RF09, RF22, RN01, RN02, RN08 |
| PB07 | Como voluntário, quero listar e filtrar o estoque, para encontrar produtos rapidamente. | 5 | 3 | RF07, RF20 |
| PB08 | Como voluntário, quero alertas de validade e o descarte de vencidos, para evitar entregas indevidas. | 5 | 4 | RF08, RF10, RN03 |
| PB09 | Como solicitante, quero pedir produtos e ver minha posição na fila, para saber quando serei atendido. | 8 | 4 | RF11, RF12, RF15, RN04 |
| PB10 | Como administrador, quero aprovar ou reprovar pedidos na ordem da fila, com baixa automática no estoque. | 8 | 4 | RF13, RF14, RN05, RN06, RN07 |
| PB11 | Como administrador, quero relatórios e indicadores, para prestar contas aos doadores. | 8 | 5 | RF16, RF17, RF18, RF19 |
| PB12 | Como equipe, queremos testes automatizados, para garantir que as regras continuem corretas. | 5 | 5 | RNF08 |
| PB13 | Como equipe, queremos uma versão em C do controle de estoque, para aplicar a programação estruturada. | 8 | 5 | — |
| PB14 | Como equipe, queremos o relatório técnico normalizado e a apresentação, para a entrega do PIM. | 5 | 6 | — |

Total estimado: 81 pontos. A Sprint 1 foi dedicada ao levantamento de requisitos e
à modelagem, que deram origem a este backlog.

## Planejamento das Sprints

| Sprint | Meta | Itens | Tarefas (Sprint Backlog) | Responsáveis |
|--------|------|-------|--------------------------|--------------|
| 1 | Entender o problema e modelar a solução | — | Levantar requisitos e regras de negócio; elaborar DHF e casos de uso; escrever o Product Backlog. | Todos |
| 2 | Base técnica e acesso seguro | PB01 a PB03 | Estruturas de dados, persistência JSON, backup e autenticação com hash. | Henrique; Andrey |
| 3 | Cadastros e entrada de doações | PB04 a PB07 | Telas de cadastro; registro de doação; listagem em árvore binária; filtros. | Andrey; Ricardo |
| 4 | Distribuição justa | PB08 a PB10 | Alertas e descarte; fila de solicitações; aprovação com baixa PVPS. | Henrique; Caio |
| 5 | Gestão e qualidade | PB11 a PB13 | Relatórios e indicadores; testes automatizados; versão em C. | Ricardo; Henrique; Andrey |
| 6 | Entrega | PB14 | Relatório técnico ABNT; diagramas finais; slides e ensaio da apresentação. | Todos |

## Definição de pronto

Um item só é considerado pronto quando:

- [ ] o código está em uma branch própria e foi integrado à `main` por pull request revisado por outro integrante;
- [ ] os testes automatizados existentes continuam passando e as novas regras de negócio possuem testes;
- [ ] entradas inválidas (texto no lugar de número, datas impossíveis, opções inexistentes) são tratadas sem encerrar o programa;
- [ ] funções e módulos estão comentados, explicando o propósito de cada trecho;
- [ ] a funcionalidade foi demonstrada em execução na Sprint Review.
