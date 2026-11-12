# Controle de Demandas de Mudanças

Sistema do DITIC-DSUP (Tribunal de Justiça do RS) para acompanhar as demandas de mudança de equipamentos de
informática, do expediente SEI à conclusão. Substitui a planilha usada hoje pelo setor.

## Como funciona

```mermaid
flowchart LR
    A([Expediente SEI chega]) --> B[Nova demanda<br/>local, datas e responsável]
    B --> C[Tickets do 4Biz<br/>ticket principal e subtickets]
    C --> D[Acionar<br/>gera o texto para o SEI]
    D -->|na Data de Início| E[Em Atendimento]
    E -->|um dia depois da<br/>Data para Conclusão| F[Para Validação]
    F --> G[Relatório de execução<br/>PDF com o custo]
    G --> H([Concluída<br/>fica com o Setor])
```

- **Nova → Acionada:** à mão, depois de registrar o ticket principal e a Data de Início.
- **Em Atendimento e Para Validação:** o sistema muda sozinho, pelas datas, sem trocar o responsável.
- **Concluída:** técnico ou coordenador conclui a partir de Para Validação. Até lá, o coordenador pode cancelar.
- **Histórico:** cada alteração fica registrada com quem fez e quando.

## Quem faz o quê

| | Técnico | Coordenador |
|---|:---:|:---:|
| Incluir, editar, acionar e concluir demandas | ✓ | ✓ |
| Gerar o texto de acionamento e o relatório em PDF | ✓ | ✓ |
| Cancelar, excluir e restaurar da lixeira | | ✓ |
| Equipe, pedidos de acesso e Configuração de valores | | ✓ |

Todos entram com usuário e senha. Quem não tem conta pede acesso na tela de entrada, e o coordenador aprova em
**Equipe**.

## Instalação

Precisa de Java 17 e MySQL 8.

1. **Banco:** no MySQL Workbench, como root, abra `db/ditic_mudancas_db.sql`, troque `TROCAR_SENHA` pela senha do
   `ditic_user` (sem salvar o arquivo) e execute. O script cria as tabelas e carrega os locais, as empresas, os
   serviços e os valores do custo.
2. **Configuração:** copie `src/main/resources/application-local.properties.exemplo` para
   `application-local.properties` e preencha a senha do banco e a senha inicial do coordenador.
3. **Aplicação:** rode `ControleMudancasApplication` no IntelliJ (ou `mvnw.cmd spring-boot:run`) e abra
   `http://localhost:8088`.
4. **Primeiro acesso:** entre com `admin` e a senha inicial, crie a sua senha e troque o nome "Coordenador" pelo seu
   em **Equipe**. Depois inclua a equipe: cada pessoa recebe uma senha temporária, válida por 24 horas.

Sem nenhum coordenador disponível, inicie a aplicação com `--mudancas.redefinir-senha=<usuário>`: a senha temporária
aparece no console.

## Testes

```bash
mvnw.cmd test                                  # testes JUnit da API e das regras (banco H2 em memória)

mvnw.cmd test-compile spring-boot:test-run     # servidor de teste, em um terminal
python src/test/e2e/teste_ponta_a_ponta.py     # teste das telas (Playwright), em outro terminal
```

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `db/` | script do banco |
| `src/main/java/` | aplicação Spring Boot: regras em `service/`, API em `controller/` |
| `src/main/resources/static/` | telas (HTML, CSS e JavaScript, com Bootstrap local) |
| `src/test/` | testes JUnit e o teste das telas |

## Tecnologias

Java 17 · Spring Boot 4 · Spring Security · MySQL · HTML, CSS e JavaScript puro · Bootstrap 5.3 · JUnit · Playwright

## Autoria

Desenvolvido por Marcelo Luis da Silva Diehl para uso do DITIC-DSUP/TJRS. Os termos de uso estão em
**Informações do Sistema**, no rodapé da aplicação.
