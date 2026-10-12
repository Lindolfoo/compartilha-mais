# Compartilha+ — Gestão de Produtos Colaborativos (Python)

Sistema em modo texto para iniciativas de doação de produtos (alimentos,
higiene, medicamentos, brinquedos, vestuário), desenvolvido para o
PIM II do CST em Análise e Desenvolvimento de Sistemas – UNIP.

## Requisitos
- Python 3.8 ou superior (apenas a biblioteca padrão; nada para instalar).

## Como executar
```bash
python main.py --demo   # cria uma base com dados fictícios para demonstração
python main.py          # executa usando a base já existente
```
Na primeira execução sem `--demo`, o sistema pede o cadastro do administrador.

Usuários da base de demonstração:

| Perfil        | Login  | Senha    |
|---------------|--------|----------|
| Administrador | admin  | admin123 |
| Voluntário    | marina | vol2025  |
| Solicitante   | ana    | ana2025  |

## Testes automatizados
```bash
python -m unittest discover -s testes -v
```

## Organização do código
| Arquivo          | Responsabilidade                                                  |
|------------------|-------------------------------------------------------------------|
| `main.py`        | Ponto de entrada, primeiro acesso e laço de login                 |
| `telas.py`       | Telas e menus por perfil (administrador, voluntário, solicitante) |
| `servicos.py`    | Regras de negócio (sem entrada/saída de tela: testável)           |
| `estruturas.py`  | Fila, pilha, árvore binária de busca, merge sort, busca binária   |
| `seguranca.py`   | Hash de senhas (PBKDF2), login com bloqueio, recuperação de senha |
| `dados.py`       | Persistência em JSON e backup automático com rotação              |
| `interface.py`   | Limpeza de tela, leitura validada, datas e tabelas responsivas    |
| `demo.py`        | Geração da base de demonstração                                   |
| `testes/`        | Testes automatizados (unittest)                                   |

Os dados ficam em `dados/base.json` e os backups em `dados/backup/`.
