-- Script de criação do banco do Controle de Demandas de Mudanças - DITIC-DSUP - TJRS
-- Rodar no MySQL como root (ou usuário com permissão de criar bancos e usuários).
-- Cria só a estrutura: o banco fica limpo, sem nenhum INSERT.
-- Pode ser executado mais de uma vez: não apaga dados existentes.
-- As tabelas que já existem não são alteradas. Se uma versão anterior deste script já foi executada,
-- e o banco ainda não tem dados, rode antes: DROP DATABASE ditic_mudancas_db;
-- Antes de rodar, troque TROCAR_SENHA pela senha do ditic_user e use a mesma em
-- src/main/resources/application-local.properties. Se o usuário já existir, a senha dele não muda.
-- O gestor "admin" não é criado aqui: a aplicação o cria ao iniciar (mudancas.admin.senha-inicial).

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS ditic_mudancas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER IF NOT EXISTS 'ditic_user'@'localhost' IDENTIFIED BY 'TROCAR_SENHA';
GRANT ALL PRIVILEGES ON ditic_mudancas_db.* TO 'ditic_user'@'localhost';
FLUSH PRIVILEGES;
USE ditic_mudancas_db;

-- ---------- pessoas ----------

-- quem usa o sistema: gestores e técnicos (a Equipe é este cadastro)
CREATE TABLE IF NOT EXISTS pessoa (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(60) NOT NULL UNIQUE,
    nome VARCHAR(60) NOT NULL UNIQUE,
    nome_curto VARCHAR(30) NOT NULL,
    iniciais CHAR(2) NOT NULL,
    cor CHAR(7) NOT NULL,                              -- #RRGGBB
    perfil ENUM('GESTOR','TECNICO') NOT NULL DEFAULT 'TECNICO',
    senha_hash VARCHAR(100) NULL,                      -- BCrypt; NULL só se a autenticação vier a ser pela rede
    deve_trocar_senha BOOLEAN NOT NULL DEFAULT TRUE,   -- primeiro acesso ou senha temporária
    senha_temporaria_expira_em DATETIME NULL,
    tentativas_falhas SMALLINT NOT NULL DEFAULT 0,
    bloqueado_ate DATETIME NULL,
    ultimo_acesso DATETIME NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- ---------- catálogos ----------

CREATE TABLE IF NOT EXISTS `local` (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL UNIQUE,                 -- 'Foro Central - Prédio I' ou 'Canoas'
    tipo ENUM('PREDIO_POA','COMARCA') NOT NULL,
    regiao VARCHAR(40) NOT NULL                        -- Metropolitana, Noroeste, Sudeste...
);

CREATE TABLE IF NOT EXISTS empresa (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(30) NOT NULL UNIQUE,                  -- CADI, CDS, Selbetti, WECOM
    paga_por_servico BOOLEAN NOT NULL                  -- CDS e WECOM = TRUE (regra da frase de custo)
);

CREATE TABLE IF NOT EXISTS servico (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    empresa_id BIGINT NOT NULL,
    nome VARCHAR(40) NOT NULL,                         -- 'Mudança de Local', 'Rollout ABC'...
    CONSTRAINT fk_servico_empresa FOREIGN KEY (empresa_id) REFERENCES empresa(id),
    UNIQUE KEY uq_servico (empresa_id, nome)
);

-- ---------- demandas ----------

CREATE TABLE IF NOT EXISTS demanda (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sei VARCHAR(20) NULL,                              -- NULL = fora do SEI
    descricao VARCHAR(250) NOT NULL,
    local_id BIGINT NULL,
    local_texto VARCHAR(120) NOT NULL,                 -- o texto digitado (o catálogo aceita texto livre)
    data_inicio DATE NULL,
    data_fim DATE NULL,
    horario TIME NULL,
    situacao ENUM('NOVA','ACIONADA','EM_ATENDIMENTO','PARA_VALIDACAO','CONCLUIDA','CANCELADA') NOT NULL DEFAULT 'NOVA',
    motivo_cancelamento VARCHAR(100) NULL,
    excluida_em DATETIME NULL,                         -- preenchido = está na lixeira; apagar depois de 30 dias
    excluida_por_id BIGINT NULL,
    motivo_exclusao VARCHAR(100) NULL,
    carga ENUM('TECNICO','GESTOR','SETOR','SEM_RESPONSAVEL') NOT NULL,  -- GESTOR = carga compartilhada por todos os gestores
    tecnico_id BIGINT NULL,                            -- responsável (carga TECNICO) ou quem atendeu (GESTOR/SETOR)
    ticket_principal VARCHAR(8) NULL,
    ticket_em DATETIME NULL,
    ticket_por_id BIGINT NULL,
    acionada_em DATE NULL,
    informacoes VARCHAR(100) NULL,
    aviso_tipo ENUM('NOVA','RETORNOU','ATENDIMENTO','PARA_VALIDACAO','STATUS') NULL,
    aviso_para VARCHAR(60) NULL,                       -- 'GESTOR' ou id do técnico
    aviso_em DATETIME NULL,
    criada_em DATETIME NOT NULL,
    atualizada_em DATETIME NOT NULL,
    CONSTRAINT fk_demanda_local FOREIGN KEY (local_id) REFERENCES `local`(id),
    CONSTRAINT fk_demanda_tecnico FOREIGN KEY (tecnico_id) REFERENCES pessoa(id),
    CONSTRAINT fk_demanda_ticket_por FOREIGN KEY (ticket_por_id) REFERENCES pessoa(id),
    CONSTRAINT fk_demanda_excluida_por FOREIGN KEY (excluida_por_id) REFERENCES pessoa(id),
    INDEX idx_demanda_situacao (situacao),
    INDEX idx_demanda_data_inicio (data_inicio),
    INDEX idx_demanda_sei (sei)
);

-- decide entre os avisos "nova" e "retornou"
CREATE TABLE IF NOT EXISTS demanda_tecnico_passou (
    demanda_id BIGINT NOT NULL,
    tecnico_id BIGINT NOT NULL,
    PRIMARY KEY (demanda_id, tecnico_id),
    CONSTRAINT fk_passou_demanda FOREIGN KEY (demanda_id) REFERENCES demanda(id) ON DELETE CASCADE,
    CONSTRAINT fk_passou_tecnico FOREIGN KEY (tecnico_id) REFERENCES pessoa(id)
);

CREATE TABLE IF NOT EXISTS subticket (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    demanda_id BIGINT NOT NULL,
    empresa_id BIGINT NOT NULL,
    numero VARCHAR(8) NOT NULL,
    servico_id BIGINT NULL,
    quantidade SMALLINT NOT NULL DEFAULT 1,
    metro_linear INT NULL,                             -- só WECOM em Instalação ou Infraestrutura; opcional
    CONSTRAINT ck_subticket_quantidade CHECK (quantidade BETWEEN 1 AND 999),
    CONSTRAINT ck_subticket_metro CHECK (metro_linear IS NULL OR metro_linear BETWEEN 1 AND 9999),
    CONSTRAINT fk_subticket_demanda FOREIGN KEY (demanda_id) REFERENCES demanda(id) ON DELETE CASCADE,
    CONSTRAINT fk_subticket_empresa FOREIGN KEY (empresa_id) REFERENCES empresa(id),
    CONSTRAINT fk_subticket_servico FOREIGN KEY (servico_id) REFERENCES servico(id),
    UNIQUE KEY uq_subticket (demanda_id, numero)
);

CREATE TABLE IF NOT EXISTS historico (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    demanda_id BIGINT NOT NULL,
    data_hora DATETIME NOT NULL,
    autor_id BIGINT NULL,                              -- quem fez a alteração; NULL = o sistema (automático)
    tipo ENUM('CRIACAO','STATUS','STATUS_AUTOMATICO','RESPONSAVEL','AGENDAMENTO','DADOS',
              'TICKET','SUBTICKET','DOCUMENTO','NOTA') NOT NULL,
    texto VARCHAR(500) NOT NULL,
    CONSTRAINT fk_historico_demanda FOREIGN KEY (demanda_id) REFERENCES demanda(id) ON DELETE CASCADE,
    CONSTRAINT fk_historico_autor FOREIGN KEY (autor_id) REFERENCES pessoa(id),
    INDEX idx_historico_data_hora (data_hora)          -- Movimentações do dia
);

-- auditoria da exclusão; demanda_id não tem chave estrangeira porque o registro sobrevive à remoção definitiva
CREATE TABLE IF NOT EXISTS demanda_excluida (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    demanda_id BIGINT NOT NULL,
    sei VARCHAR(20) NULL,
    local_texto VARCHAR(120) NULL,
    situacao VARCHAR(20) NOT NULL,
    excluida_em DATETIME NOT NULL,
    excluida_por_id BIGINT NULL,                       -- NULL = o sistema (remoção definitiva após 30 dias)
    motivo VARCHAR(100) NULL,
    texto VARCHAR(250) NULL,                           -- usado na remoção definitiva
    CONSTRAINT fk_excluida_por FOREIGN KEY (excluida_por_id) REFERENCES pessoa(id),
    INDEX idx_excluida_em (excluida_em)                -- Movimentações do dia
);

-- ---------- valores do custo do relatório (tela Configuração) ----------

-- preço da CDS por região e serviço
CREATE TABLE IF NOT EXISTS preco_cds (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    regiao VARCHAR(40) NOT NULL,
    servico_id BIGINT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_preco_cds_servico FOREIGN KEY (servico_id) REFERENCES servico(id),
    UNIQUE KEY uq_preco_cds (regiao, servico_id)
);

-- valores avulsos da WECOM: WECOM_REALOCACAO, WECOM_INSTALACAO (Instalação/Infraestrutura) e WECOM_METRO_LINEAR
CREATE TABLE IF NOT EXISTS preco_parametro (
    chave VARCHAR(40) PRIMARY KEY,
    valor DECIMAL(10,2) NOT NULL
);
