# Orientação para o Claude Code

**Controle de Demandas de Mudanças** (DITIC-DSUP / TJRS): telas em HTML, CSS e JavaScript puro, back-end Java 17 +
Spring Boot 4 e banco MySQL. As regras de negócio estão no código (`service/`) e nos testes; o `README.md` traz o
uso e o fluxo.

**Organização**
- Idioma: tudo em português do Brasil (textos da tela, nomes no código, comentários, commits).
- Banco: `db/ditic_mudancas_db.sql` cria as tabelas e carrega catálogos e valores iniciais (entre as marcas
  `[dados-iniciais]`). Todo dado editável vem do banco; nada de dados de exemplo no código. As entidades JPA seguem o
  script (`ddl-auto=validate`).
- Regras de status, permissão e custo ficam no servidor (`service/`); a tela só orienta e esconde botões.
- Telas: uma cópia só, em `src/main/resources/static/` (`index.html`, `css/mudancas.css`, `js/mudancas.js`, Bootstrap
  5.3.3 em `vendor/`, fontes em `fonts/`). Sem build e sem recursos externos. Todo dado que entra no HTML passa por
  `esc()`; toda chamada ao servidor passa por `api()`, e as alterações por `acao()`.
- Testes: `mvnw test` (JUnit, banco H2) e `python src/test/e2e/teste_ponta_a_ponta.py` (telas), este com o servidor de
  teste no ar (`mvnw test-compile spring-boot:test-run`, reiniciado a cada rodada).
- O repositório é público: nunca colocar senhas em arquivos versionados (`application-local.properties` fica fora do Git).

**Decisões já tomadas com o setor (não reverter sem falar com o autor)**
- Visual: o tema fica sobre o Bootstrap (variáveis `--bs-*`). Não mudar o visual sem pedido explícito; "revisões
  visuais" amplas foram rejeitadas. Modais fecham só pelo X ou pelos botões, nunca por clique fora ou Esc.
- Fluxo: Pendente (no banco, `NOVA`) → Acionada (à mão, exige ticket principal e Data de Início; volta à mão para
  Pendente, mantendo tickets e datas) → Em Atendimento (na Data de Início) →
  Para Validação (um dia depois da Data para Conclusão) → Concluída (fica com o Setor). Sozinha, Para Validação nunca
  volta; com as datas remarcadas (Em Atendimento ou Para Validação), vai para Acionada (início no futuro) ou Em Atendimento.
  A mudança automática não troca o responsável. Concluída e Cancelada são finais e somente leitura.
- Perfis: sem login, só consulta (lista, cards e histórico; sem custo, valores e dados das contas). Alterar exige
  login, e a Nova demanda só aparece depois de entrar. O técnico faz tudo nas demandas; só o administrador cancela, exclui, restaura da lixeira,
  aprova acessos e mantém Equipe e Configuração. Toda demanda tem responsável (no mínimo, o Administrador, carga
  compartilhada); a demanda nova vai sempre para um técnico escolhido (sem pré-seleção e sem o Administrador); só a Concluída fica com o Setor. Administrador é um só (a conta `admin`; por dentro, perfil e carga
  continuam `COORDENADOR`); toda conta nova é de técnico. Nome com até 30 caracteres; usuário da rede com até 20. Na tela não aparece mais "Coordenador".
  Excluir técnico: transfere as abertas; sem nenhum registro, apaga; com registro, só desativa (o histórico fica).
- Sistema em produção com dados reais: nenhuma mudança na estrutura do banco (tabelas, colunas, ENUMs) sem combinar.
  Mudança combinada vai também num script `db/atualizacao_*.sql`, rodado no banco em uso antes de trocar o .jar.
- Tickets: principal e subtickets com 7 dígitos. Subticket é único entre todas as demandas (repetido bloqueia)
  e tem descrição opcional (1000 caracteres; só no card; o histórico registra só que foi incluída, alterada
  ou removida). Informações adicionais: 250 caracteres.
  Ticket principal ou SEI repetido só avisam. Local só da lista do catálogo.
- Custo do relatório: CDS = quantidade × preço da região; WECOM Realocação e Instalação = quantidade × valor;
  Infraestrutura = metro linear × valor do metro (a quantidade não multiplica) ou, sem metro, uma verba de 15 m por
  ticket. O check "Somar a Infraestrutura" desmarcado tira o valor e troca a observação por uma frase única.
- Textos: a informação de acionamento sai em blocos (Agendamento / Tickets); o relatório termina sempre com
  "Era o que cabia informar.".
