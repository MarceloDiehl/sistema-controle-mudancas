# Controle de Demandas de Mudanças

Sistema do Departamento de Suporte (DSUP) da DITIC, no Tribunal de Justiça do Rio Grande do Sul, para acompanhar
as demandas de mudança de equipamentos de informática, do expediente SEI à conclusão. Vai substituir a planilha
usada hoje pelo setor.

> **Situação:** as telas estão prontas (versão 1.0.0) e guardam os dados no navegador, com login de demonstração.
> O back-end em Spring Boot e MySQL está em construção.

## Funcionalidades

- Cadastro de demandas por expediente SEI, com local, período e responsável
- Tickets principais e subtickets do 4Biz, por empresa contratada e serviço
- Mudança automática de status conforme as datas do agendamento
- Contagem dos dias até o início do atendimento
- Histórico de cada demanda e movimentações do dia
- Lixeira com restauração em até 30 dias
- Texto de acionamento para o SEI e relatório de execução em PDF
- Custo do relatório calculado para CDS e WECOM, com valores editáveis pelo gestor

**Fluxo de status:** Nova → Acionada → Em Atendimento → Para Validação → Concluída. Até a conclusão, o gestor pode
cancelar a demanda.

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Telas | HTML, CSS e JavaScript puro, com Bootstrap 5.3 local |
| Back-end | Java 17, Spring Boot 4 e Spring Security |
| Banco de dados | MySQL |
| Testes | JUnit e Playwright |

## Como executar

**Somente as telas:** abra `front_end/index.html` em um navegador atual. Não precisa de instalação nem de internet.
No primeiro acesso, entre com o usuário `admin` e qualquer senha.

**Com o Spring Boot:** é preciso ter Java 17 e MySQL.

1. Copie `src/main/resources/application-local.properties.exemplo` para `application-local.properties`, na mesma
   pasta, e preencha os dados de acesso.
2. Rode `./mvnw spring-boot:run` (no Windows, `mvnw.cmd spring-boot:run`).
3. Acesse `http://localhost:8088`.

## Testes

```bash
./mvnw test                                   # aplicação Spring Boot

pip install playwright
python -m playwright install chromium
python front_end/testes/teste_ponta_a_ponta.py   # fluxos das telas
```

## Estrutura

```
docs/ESPECIFICACAO.md      regras de negócio, telas, modelo de dados e API
front_end/                 telas do sistema e teste de ponta a ponta
src/main/java/             aplicação Spring Boot
src/main/resources/static/ cópia das telas servida pelo Spring Boot
db/                        scripts do banco (em construção)
```

## Próximos passos

1. Banco de dados e API, com as regras de status e permissão no servidor
2. Login individual para gestores e técnicos
3. Status automáticos e limpeza da lixeira no servidor
4. Integração das telas com a API

As regras completas estão em [docs/ESPECIFICACAO.md](docs/ESPECIFICACAO.md).

## Autoria

Desenvolvido por Marcelo Luis da Silva Diehl para uso do DITIC-DSUP/TJRS. Os termos de uso estão em
**Informações do Sistema**, no rodapé da aplicação.
