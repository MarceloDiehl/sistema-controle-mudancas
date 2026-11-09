# Orientação para o Claude Code

Protótipo do **Controle de Demandas de Mudanças** (DITIC-DSUP / TJRS). A especificação completa está em
`README.md`: proposta, fluxo, regras de negócio, telas, modelo de dados, banco sugerido, API e as
decisões já tomadas com o setor. Leia o README antes de mudar qualquer coisa.

- Sem build e sem dependências online: `index.html` + `css/mudancas.css` + `js/mudancas.js`, com o
  Bootstrap 5.3.3 em `vendor/` e as fontes em `fonts/`. Abre direto no navegador.
- Idioma: tudo em português do Brasil (textos da tela, nomes no código, comentários, commits).
- Visual: o tema fica sobre o Bootstrap (variáveis `--bs-*` em `css/mudancas.css`). Não mude o visual
  sem pedido explícito; o autor rejeita "revisões visuais" amplas (ver README, seção 14).
- JS: todo dado que entra no HTML passa por `esc()`; nada de `eval` ou recursos externos. Os pontos de
  integração com o back-end estão marcados com `// API:`.
- Back-end previsto: Java/Spring Boot + MySQL (README, seções 11 e 12). As regras de status e
  permissão devem ser validadas no servidor.
- Teste automático: `python testes/teste_ponta_a_ponta.py` (Python + Playwright).
