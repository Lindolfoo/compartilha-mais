# Requisitos e regras de negócio

Especificação do Capítulo 4 do relatório técnico. As regras de negócio são
validadas em `python/servicos.py` e cobertas por `python/testes/test_sistema.py`.

## Requisitos funcionais

| ID | Descrição | Área do escopo |
|----|-----------|----------------|
| RF01 | Autenticar usuários com três níveis de acesso: administrador, voluntário e solicitante. | Login |
| RF02 | Bloquear o usuário após três tentativas de senha incorretas; o administrador pode desbloqueá-lo. | Login |
| RF03 | Recuperar a senha por pergunta de segurança e permitir a troca de senha. | Login |
| RF04 | Cadastrar produtos com nome, categoria, quantidade, unidade, peso, validade, lote e doador de origem. | Cadastro |
| RF05 | Cadastrar doadores e solicitantes com dados pessoais (CPF ou CNPJ) e de contato. | Cadastro |
| RF06 | Cadastrar funcionários e voluntários com acesso ao sistema, garantindo a rastreabilidade. | Cadastro |
| RF07 | Exibir os produtos disponíveis em ordem alfabética, com saldo e dias até o vencimento. | Estoque |
| RF08 | Alertar produtos vencidos e que vencem em até 30 dias, em ordem de urgência. | Estoque |
| RF09 | Atualizar as quantidades automaticamente a cada doação, entrega e descarte. | Estoque |
| RF10 | Registrar o descarte de produtos vencidos, retirando-os do estoque disponível. | Estoque |
| RF11 | Registrar pedidos de produtos, feitos pelo solicitante ou por um voluntário em seu nome. | Solicitações |
| RF12 | Organizar os pedidos pendentes em fila por ordem de chegada. | Solicitações |
| RF13 | Aprovar ou reprovar pedidos (reprovação com motivo obrigatório). | Solicitações |
| RF14 | Baixar o estoque dos lotes que vencem primeiro (PVPS) ao aprovar um pedido. | Solicitações |
| RF15 | Exibir o histórico de atendimentos de cada solicitante e a posição na fila. | Solicitações |
| RF16 | Gerar relatório de entradas e saídas por período. | Relatórios |
| RF17 | Gerar relatório dos produtos mais solicitados. | Relatórios |
| RF18 | Gerar relatórios de doações por período (mensal) e por doador. | Relatórios |
| RF19 | Calcular indicadores de aproveitamento, perda, aprovação e tempo de espera. | Relatórios |
| RF20 | Buscar produtos com filtros combináveis: início do nome, categoria e prazo de validade. | Complementar |
| RF21 | Fazer backup automático a cada gravação e permitir a restauração. | Complementar |
| RF22 | Listar as ações da sessão e desfazer a última doação registrada. | Complementar |

## Requisitos não funcionais

| ID | Categoria | Descrição e forma de atendimento |
|----|-----------|----------------------------------|
| RNF01 | Usabilidade | Menus numerados, mensagens padronizadas (`[OK]`, `[ERRO]`, `[!]`) e validação de todos os campos. |
| RNF02 | Responsividade | Cabeçalhos e tabelas ajustam-se à largura do terminal (entre 60 e 100 colunas). |
| RNF03 | Acessibilidade | Interface somente em texto, legível por leitores de tela; nenhuma informação depende apenas de cor. |
| RNF04 | Segurança | Senhas armazenadas apenas como hash PBKDF2 com sal aleatório e 100.000 iterações; comparação em tempo constante. |
| RNF05 | Confiabilidade | Gravação atômica, backup rotativo dos cinco últimos estados e recuperação automática de arquivo corrompido. |
| RNF06 | Desempenho | Cadastro, busca e aprovação em menos de 1 segundo para milhares de registros. |
| RNF07 | Portabilidade | Windows e Linux, apenas com a biblioteca padrão do Python 3.8+ e compilador C99. |
| RNF08 | Manutenibilidade | Regras de negócio separadas das telas, permitindo testes automatizados; código comentado. |

## Regras de negócio

| ID | Regra |
|----|-------|
| RN01 | Produtos das categorias Alimentos, Higiene e Medicamentos só podem ser recebidos com data de validade. |
| RN02 | Não é permitido receber produto já vencido. |
| RN03 | Lotes vencidos deixam de aparecer como disponíveis e só podem ser descartados. |
| RN04 | Cada solicitante pode ter apenas uma solicitação pendente por produto. |
| RN05 | As solicitações são avaliadas estritamente na ordem de chegada (fila). |
| RN06 | A reprovação de uma solicitação exige o registro do motivo. |
| RN07 | Na aprovação, a baixa é feita primeiro nos lotes que vencem antes (PVPS – primeiro que vence, primeiro que sai). |
| RN08 | Uma doação só pode ser desfeita se o lote ainda não tiver nenhuma saída ou descarte. |
| RN09 | O documento do doador ou solicitante deve ter 11 (CPF) ou 14 (CNPJ) dígitos e é único por tipo de cadastro. |
