# Como contribuir

1. Escolha uma *issue* do Product Backlog (milestone da Sprint atual) e atribua-a a você.
2. Crie a branch a partir da `main`: `git switch -c feature/<nome>`.
3. Faça commits pequenos no padrão `tipo: descrição`, em que o tipo é
   `feat` (funcionalidade), `fix` (correção), `test` (testes), `docs`
   (documentação) ou `chore` (manutenção).
4. Rode os testes antes de enviar:
   ```bash
   cd python && python -m unittest discover -s testes -v
   cd c && make
   ```
5. Abra um *pull request* para a `main` citando a issue (`Closes #n`).
6. Outro integrante revisa; o merge só acontece com a revisão aprovada e os
   testes do GitHub Actions passando, conforme a
   [definição de pronto](docs/scrum/README.md#definição-de-pronto).
