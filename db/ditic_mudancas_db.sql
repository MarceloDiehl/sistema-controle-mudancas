-- Script do banco do Controle de Demandas de Mudanças - DITIC-DSUP - TJRS
-- Rodar no MySQL Workbench como root (ou usuário com permissão de criar bancos e usuários).
-- Cria a estrutura e carrega os catálogos (locais, empresas, serviços) e os valores iniciais do custo do relatório.
-- Pode ser executado mais de uma vez: não apaga nem altera dados existentes (as tabelas e linhas que já existem ficam
-- como estão). Se uma versão anterior deste script já foi executada e o banco ainda não tem dados, rode antes:
--     DROP DATABASE ditic_mudancas_db;
-- Antes de rodar, troque TROCAR_SENHA pela senha do ditic_user (sem salvar o arquivo com a senha) e use a mesma em
-- src/main/resources/application-local.properties. Se o usuário já existir, a senha dele não muda.
-- O coordenador "admin" não é criado aqui: a aplicação o cria ao iniciar (mudancas.admin.senha-inicial).

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS ditic_mudancas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER IF NOT EXISTS 'ditic_user'@'localhost' IDENTIFIED BY 'TROCAR_SENHA';
GRANT ALL PRIVILEGES ON ditic_mudancas_db.* TO 'ditic_user'@'localhost';
FLUSH PRIVILEGES;
USE ditic_mudancas_db;

-- ---------- pessoas ----------

-- quem usa o sistema: coordenadores e técnicos (a Equipe é este cadastro)
CREATE TABLE IF NOT EXISTS pessoa (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(60) NOT NULL UNIQUE,
    nome VARCHAR(60) NOT NULL UNIQUE,
    nome_curto VARCHAR(30) NOT NULL,
    iniciais CHAR(2) NOT NULL,
    cor CHAR(7) NOT NULL,                              -- #RRGGBB
    perfil ENUM('COORDENADOR','TECNICO') NOT NULL DEFAULT 'TECNICO',
    senha_hash VARCHAR(100) NULL,                      -- BCrypt; NULL só se a autenticação vier a ser pela rede
    deve_trocar_senha BOOLEAN NOT NULL DEFAULT TRUE,   -- primeiro acesso ou senha temporária
    senha_temporaria_expira_em DATETIME NULL,
    tentativas_falhas SMALLINT NOT NULL DEFAULT 0,
    bloqueado_ate DATETIME NULL,
    ultimo_acesso DATETIME NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- pedidos de acesso feitos na tela de login; o coordenador aprova (cria a pessoa) ou recusa
CREATE TABLE IF NOT EXISTS solicitacao_acesso (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(60) NOT NULL,
    nome VARCHAR(60) NOT NULL,
    pedida_em DATETIME NOT NULL,
    situacao ENUM('PENDENTE','APROVADA','RECUSADA') NOT NULL DEFAULT 'PENDENTE',
    decidida_por BIGINT NULL,                          -- coordenador que aprovou ou recusou
    decidida_em DATETIME NULL,
    pessoa_id BIGINT NULL,                             -- conta criada na aprovação
    CONSTRAINT fk_solicitacao_decidida_por FOREIGN KEY (decidida_por) REFERENCES pessoa(id),
    CONSTRAINT fk_solicitacao_pessoa FOREIGN KEY (pessoa_id) REFERENCES pessoa(id),
    INDEX idx_solicitacao_situacao (situacao)
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
    local_id BIGINT NULL,                              -- local escolhido na lista (catálogo)
    local_texto VARCHAR(120) NOT NULL,                 -- nome do local, como estava quando foi escolhido
    data_inicio DATE NULL,
    data_fim DATE NULL,
    horario TIME NULL,
    situacao ENUM('NOVA','ACIONADA','EM_ATENDIMENTO','PARA_VALIDACAO','CONCLUIDA','CANCELADA') NOT NULL DEFAULT 'NOVA',
    motivo_cancelamento VARCHAR(100) NULL,
    excluida_em DATETIME NULL,                         -- preenchido = está na lixeira; apagar depois de 30 dias
    excluida_por_id BIGINT NULL,
    motivo_exclusao VARCHAR(100) NULL,
    carga ENUM('TECNICO','COORDENADOR','SETOR') NOT NULL,  -- sempre há responsável (no mínimo COORDENADOR, compartilhada); SETOR só na concluída
    tecnico_id BIGINT NULL,                            -- responsável (carga TECNICO) ou quem atendeu (COORDENADOR/SETOR)
    ticket_principal CHAR(8) NULL,                     -- sempre 8 dígitos
    ticket_em DATETIME NULL,
    ticket_por_id BIGINT NULL,
    acionada_em DATE NULL,
    informacoes VARCHAR(100) NULL,
    aviso_tipo ENUM('NOVA','RETORNOU','ATENDIMENTO','PARA_VALIDACAO','STATUS') NULL,
    aviso_para VARCHAR(60) NULL,                       -- 'COORDENADOR' ou id do técnico
    aviso_em DATETIME NULL,
    criada_em DATETIME NOT NULL,
    atualizada_em DATETIME NOT NULL,
    CONSTRAINT ck_demanda_ticket CHECK (ticket_principal IS NULL OR ticket_principal REGEXP '^[0-9]{8}$'),
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
    numero CHAR(8) NOT NULL,                           -- sempre 8 dígitos; único entre todas as demandas
    servico_id BIGINT NULL,
    quantidade SMALLINT NOT NULL DEFAULT 1,
    metro_linear INT NULL,                             -- só WECOM em Infraestrutura; opcional
    CONSTRAINT ck_subticket_numero CHECK (numero REGEXP '^[0-9]{8}$'),
    CONSTRAINT ck_subticket_quantidade CHECK (quantidade BETWEEN 1 AND 999),
    CONSTRAINT ck_subticket_metro CHECK (metro_linear IS NULL OR metro_linear BETWEEN 1 AND 9999),
    CONSTRAINT fk_subticket_demanda FOREIGN KEY (demanda_id) REFERENCES demanda(id) ON DELETE CASCADE,
    CONSTRAINT fk_subticket_empresa FOREIGN KEY (empresa_id) REFERENCES empresa(id),
    CONSTRAINT fk_subticket_servico FOREIGN KEY (servico_id) REFERENCES servico(id),
    UNIQUE KEY uq_subticket_numero (numero)
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
    INDEX idx_historico_data_hora (data_hora)
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
    INDEX idx_excluida_em (excluida_em)
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

-- valores avulsos da WECOM: WECOM_REALOCACAO, WECOM_INSTALACAO e WECOM_METRO_LINEAR
-- (a verba da Infraestrutura sem metro linear usa 15 metros, valor fixo da aplicação)
CREATE TABLE IF NOT EXISTS preco_parametro (
    chave VARCHAR(40) PRIMARY KEY,
    valor DECIMAL(10,2) NOT NULL
);

-- ==================================================================================================
-- Dados iniciais. A tela Configuração altera os valores; locais, empresas e serviços são catálogos.
-- (O teste automático carrega este trecho, entre as marcas [dados-iniciais] e [/dados-iniciais].)
-- [dados-iniciais]

-- locais: os 13 prédios de Porto Alegre (região Metropolitana) e as 164 comarcas do interior
INSERT IGNORE INTO `local` (nome, tipo, regiao) VALUES
    ('Tribunal de Justiça', 'PREDIO_POA', 'Metropolitana'),
    ('Tribunal de Justiça - Anexo', 'PREDIO_POA', 'Metropolitana'),
    ('Palácio da Justiça', 'PREDIO_POA', 'Metropolitana'),
    ('Foro Central - Prédio I', 'PREDIO_POA', 'Metropolitana'),
    ('Foro Central - Prédio II', 'PREDIO_POA', 'Metropolitana'),
    ('Foro Regional da Restinga', 'PREDIO_POA', 'Metropolitana'),
    ('Foro Regional da Tristeza', 'PREDIO_POA', 'Metropolitana'),
    ('Foro Regional da Zona Leste', 'PREDIO_POA', 'Metropolitana'),
    ('Foro Regional da Zona Norte', 'PREDIO_POA', 'Metropolitana'),
    ('Foro Regional do Alto Petrópolis', 'PREDIO_POA', 'Metropolitana'),
    ('Foro Regional do Partenon', 'PREDIO_POA', 'Metropolitana'),
    ('Foro Regional do Sarandi', 'PREDIO_POA', 'Metropolitana'),
    ('Transporte - Garagem', 'PREDIO_POA', 'Metropolitana'),
    ('Agudo', 'COMARCA', 'Centro Ocidental'),
    ('Alegrete', 'COMARCA', 'Sudoeste'),
    ('Alvorada', 'COMARCA', 'Metropolitana'),
    ('Antônio Prado', 'COMARCA', 'Nordeste'),
    ('Arroio do Meio', 'COMARCA', 'Centro Oriental'),
    ('Arroio do Tigre', 'COMARCA', 'Centro Oriental'),
    ('Arroio Grande', 'COMARCA', 'Sudeste'),
    ('Arvorezinha', 'COMARCA', 'Nordeste'),
    ('Augusto Pestana', 'COMARCA', 'Noroeste'),
    ('Bagé', 'COMARCA', 'Sudoeste'),
    ('Barra do Ribeiro', 'COMARCA', 'Metropolitana'),
    ('Bento Gonçalves', 'COMARCA', 'Nordeste'),
    ('Bom Jesus', 'COMARCA', 'Nordeste'),
    ('Butiá', 'COMARCA', 'Metropolitana'),
    ('Caçapava do Sul', 'COMARCA', 'Sudeste'),
    ('Cacequi', 'COMARCA', 'Centro Ocidental'),
    ('Cachoeira do Sul', 'COMARCA', 'Centro Oriental'),
    ('Cachoeirinha', 'COMARCA', 'Metropolitana'),
    ('Camaquã', 'COMARCA', 'Metropolitana'),
    ('Campina das Missões', 'COMARCA', 'Noroeste'),
    ('Campo Bom', 'COMARCA', 'Metropolitana'),
    ('Campo Novo', 'COMARCA', 'Noroeste'),
    ('Candelária', 'COMARCA', 'Centro Oriental'),
    ('Canela', 'COMARCA', 'Metropolitana'),
    ('Canguçu', 'COMARCA', 'Sudeste'),
    ('Canoas', 'COMARCA', 'Metropolitana'),
    ('Capão da Canoa', 'COMARCA', 'Metropolitana'),
    ('Carazinho', 'COMARCA', 'Noroeste'),
    ('Carlos Barbosa', 'COMARCA', 'Nordeste'),
    ('Casca', 'COMARCA', 'Noroeste'),
    ('Catuipe', 'COMARCA', 'Noroeste'),
    ('Caxias do Sul', 'COMARCA', 'Nordeste'),
    ('Cerro Largo', 'COMARCA', 'Noroeste'),
    ('Charqueadas', 'COMARCA', 'Metropolitana'),
    ('Constantina', 'COMARCA', 'Noroeste'),
    ('Coronel Bicaco', 'COMARCA', 'Noroeste'),
    ('Crissiumal', 'COMARCA', 'Noroeste'),
    ('Cruz Alta', 'COMARCA', 'Noroeste'),
    ('Dois Irmãos', 'COMARCA', 'Metropolitana'),
    ('Dom Pedrito', 'COMARCA', 'Sudoeste'),
    ('Eldorado do Sul', 'COMARCA', 'Metropolitana'),
    ('Encantado', 'COMARCA', 'Centro Oriental'),
    ('Encruzilhada do Sul', 'COMARCA', 'Sudeste'),
    ('Erechim', 'COMARCA', 'Noroeste'),
    ('Espumoso', 'COMARCA', 'Noroeste'),
    ('Estância Velha', 'COMARCA', 'Metropolitana'),
    ('Esteio', 'COMARCA', 'Metropolitana'),
    ('Estrela', 'COMARCA', 'Centro Oriental'),
    ('Farroupilha', 'COMARCA', 'Nordeste'),
    ('Faxinal do Soturno', 'COMARCA', 'Centro Ocidental'),
    ('Feliz', 'COMARCA', 'Metropolitana'),
    ('Flores da Cunha', 'COMARCA', 'Nordeste'),
    ('Frederico Westphalen', 'COMARCA', 'Noroeste'),
    ('Garibaldi', 'COMARCA', 'Nordeste'),
    ('Gaurama', 'COMARCA', 'Noroeste'),
    ('General Câmara', 'COMARCA', 'Metropolitana'),
    ('Getúlio Vargas', 'COMARCA', 'Noroeste'),
    ('Giruá', 'COMARCA', 'Noroeste'),
    ('Gramado', 'COMARCA', 'Metropolitana'),
    ('Gravataí', 'COMARCA', 'Metropolitana'),
    ('Guaíba', 'COMARCA', 'Metropolitana'),
    ('Guaporé', 'COMARCA', 'Nordeste'),
    ('Guarani das Missões', 'COMARCA', 'Noroeste'),
    ('Herval', 'COMARCA', 'Sudeste'),
    ('Horizontina', 'COMARCA', 'Noroeste'),
    ('Ibirubá', 'COMARCA', 'Noroeste'),
    ('Igrejinha', 'COMARCA', 'Metropolitana'),
    ('Ijuí', 'COMARCA', 'Noroeste'),
    ('Iraí', 'COMARCA', 'Noroeste'),
    ('Itaqui', 'COMARCA', 'Sudoeste'),
    ('Ivoti', 'COMARCA', 'Metropolitana'),
    ('Jaguarão', 'COMARCA', 'Sudeste'),
    ('Jaguari', 'COMARCA', 'Centro Ocidental'),
    ('Júlio de Castilhos', 'COMARCA', 'Centro Ocidental'),
    ('Lagoa Vermelha', 'COMARCA', 'Nordeste'),
    ('Lajeado', 'COMARCA', 'Centro Oriental'),
    ('Lavras do Sul', 'COMARCA', 'Sudoeste'),
    ('Marau', 'COMARCA', 'Noroeste'),
    ('Marcelino Ramos', 'COMARCA', 'Noroeste'),
    ('Montenegro', 'COMARCA', 'Metropolitana'),
    ('Mostardas', 'COMARCA', 'Metropolitana'),
    ('Não Me Toque', 'COMARCA', 'Noroeste'),
    ('Nonoai', 'COMARCA', 'Noroeste'),
    ('Nova Petrópolis', 'COMARCA', 'Metropolitana'),
    ('Nova Prata', 'COMARCA', 'Nordeste'),
    ('Novo Hamburgo', 'COMARCA', 'Metropolitana'),
    ('Osório', 'COMARCA', 'Metropolitana'),
    ('Palmares do Sul', 'COMARCA', 'Metropolitana'),
    ('Palmeira das Missões', 'COMARCA', 'Noroeste'),
    ('Panambi', 'COMARCA', 'Noroeste'),
    ('Parobé', 'COMARCA', 'Metropolitana'),
    ('Passo Fundo', 'COMARCA', 'Noroeste'),
    ('Pedro Osório', 'COMARCA', 'Sudeste'),
    ('Pelotas', 'COMARCA', 'Sudeste'),
    ('Pinheiro Machado', 'COMARCA', 'Sudeste'),
    ('Piratini', 'COMARCA', 'Sudeste'),
    ('Planalto', 'COMARCA', 'Noroeste'),
    ('Portão', 'COMARCA', 'Metropolitana'),
    ('Porto Xavier', 'COMARCA', 'Noroeste'),
    ('Quaraí', 'COMARCA', 'Sudoeste'),
    ('Restinga Seca', 'COMARCA', 'Centro Ocidental'),
    ('Rio Grande', 'COMARCA', 'Sudeste'),
    ('Rio Pardo', 'COMARCA', 'Centro Oriental'),
    ('Rodeio Bonito', 'COMARCA', 'Noroeste'),
    ('Ronda Alta', 'COMARCA', 'Noroeste'),
    ('Rosário do Sul', 'COMARCA', 'Sudoeste'),
    ('Salto do Jacuí', 'COMARCA', 'Noroeste'),
    ('Sananduva', 'COMARCA', 'Noroeste'),
    ('Santa Bárbara do Sul', 'COMARCA', 'Noroeste'),
    ('Santa Cruz do Sul', 'COMARCA', 'Centro Oriental'),
    ('Santa Maria', 'COMARCA', 'Centro Ocidental'),
    ('Santa Rosa', 'COMARCA', 'Noroeste'),
    ('Santa Vitória do Palmar', 'COMARCA', 'Sudeste'),
    ('Santana do Livramento', 'COMARCA', 'Sudoeste'),
    ('Santiago', 'COMARCA', 'Centro Ocidental'),
    ('Santo Ângelo', 'COMARCA', 'Noroeste'),
    ('Santo Antônio da Patrulha', 'COMARCA', 'Metropolitana'),
    ('Santo Antônio das Missões', 'COMARCA', 'Noroeste'),
    ('Santo Augusto', 'COMARCA', 'Noroeste'),
    ('Santo Cristo', 'COMARCA', 'Noroeste'),
    ('São Borja', 'COMARCA', 'Sudoeste'),
    ('São Francisco de Assis', 'COMARCA', 'Sudoeste'),
    ('São Francisco de Paula', 'COMARCA', 'Nordeste'),
    ('São Gabriel', 'COMARCA', 'Sudoeste'),
    ('São Jerônimo', 'COMARCA', 'Metropolitana'),
    ('São José do Norte', 'COMARCA', 'Sudeste'),
    ('São José do Ouro', 'COMARCA', 'Noroeste'),
    ('São Leopoldo', 'COMARCA', 'Metropolitana'),
    ('São Lourenço do Sul', 'COMARCA', 'Sudeste'),
    ('São Luiz Gonzaga', 'COMARCA', 'Noroeste'),
    ('São Marcos', 'COMARCA', 'Nordeste'),
    ('São Pedro do Sul', 'COMARCA', 'Centro Ocidental'),
    ('São Sebastião do Caí', 'COMARCA', 'Metropolitana'),
    ('São Sepé', 'COMARCA', 'Centro Ocidental'),
    ('São Valentim', 'COMARCA', 'Noroeste'),
    ('São Vicente do Sul', 'COMARCA', 'Centro Ocidental'),
    ('Sapiranga', 'COMARCA', 'Metropolitana'),
    ('Sapucaia do Sul', 'COMARCA', 'Metropolitana'),
    ('Sarandi', 'COMARCA', 'Noroeste'),
    ('Seberi', 'COMARCA', 'Noroeste'),
    ('Sobradinho', 'COMARCA', 'Centro Oriental'),
    ('Soledade', 'COMARCA', 'Noroeste'),
    ('Tapejara', 'COMARCA', 'Noroeste'),
    ('Tapera', 'COMARCA', 'Noroeste'),
    ('Tapes', 'COMARCA', 'Metropolitana'),
    ('Taquara', 'COMARCA', 'Metropolitana'),
    ('Taquari', 'COMARCA', 'Centro Oriental'),
    ('Tenente Portela', 'COMARCA', 'Noroeste'),
    ('Terra de Areia', 'COMARCA', 'Metropolitana'),
    ('Teutônia', 'COMARCA', 'Centro Oriental'),
    ('Torres', 'COMARCA', 'Metropolitana'),
    ('Tramandai', 'COMARCA', 'Metropolitana'),
    ('Três Coroas', 'COMARCA', 'Metropolitana'),
    ('Três de Maio', 'COMARCA', 'Noroeste'),
    ('Três Passos', 'COMARCA', 'Noroeste'),
    ('Triunfo', 'COMARCA', 'Metropolitana'),
    ('Tucunduva', 'COMARCA', 'Noroeste'),
    ('Tupanciretã', 'COMARCA', 'Centro Ocidental'),
    ('Uruguaiana', 'COMARCA', 'Sudoeste'),
    ('Vacaria', 'COMARCA', 'Nordeste'),
    ('Venâncio Aires', 'COMARCA', 'Centro Oriental'),
    ('Vera Cruz', 'COMARCA', 'Centro Oriental'),
    ('Veranópolis', 'COMARCA', 'Nordeste'),
    ('Viamão', 'COMARCA', 'Metropolitana');

-- empresas contratadas: CDS e WECOM são pagas por serviço; CADI e Selbetti estão no valor global do contrato
INSERT IGNORE INTO empresa (nome, paga_por_servico) VALUES
    ('CADI', FALSE), ('CDS', TRUE), ('Selbetti', FALSE), ('WECOM', TRUE);

-- serviços de cada empresa, na ordem em que aparecem na escolha do subticket
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Mudança de Local' FROM empresa WHERE nome = 'CADI';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Configuração' FROM empresa WHERE nome = 'CADI';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Habilitação de Pontos de Rede' FROM empresa WHERE nome = 'CADI';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Instalação' FROM empresa WHERE nome = 'CDS';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Desinstalação' FROM empresa WHERE nome = 'CDS';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Rollout AC' FROM empresa WHERE nome = 'CDS';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Rollout ABC' FROM empresa WHERE nome = 'CDS';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Mudança de Local' FROM empresa WHERE nome = 'CDS';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Mudança de Prédio' FROM empresa WHERE nome = 'CDS';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Mudança de Local' FROM empresa WHERE nome = 'Selbetti';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Instalação' FROM empresa WHERE nome = 'Selbetti';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Desinstalação' FROM empresa WHERE nome = 'Selbetti';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Mudança de Prédio' FROM empresa WHERE nome = 'Selbetti';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Instalação' FROM empresa WHERE nome = 'WECOM';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Realocação' FROM empresa WHERE nome = 'WECOM';
INSERT IGNORE INTO servico (empresa_id, nome) SELECT id, 'Infraestrutura' FROM empresa WHERE nome = 'WECOM';

-- preço da CDS por região e serviço, na ordem do sistema de faturamento do DSUP (a Configuração mostra nesta ordem)
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Noroeste', s.id, 285.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Instalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Nordeste', s.id, 229.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Instalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Centro Ocidental', s.id, 233.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Instalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Centro Oriental', s.id, 272.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Instalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Metropolitana', s.id, 125.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Instalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Sudeste', s.id, 273.95 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Instalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Sudoeste', s.id, 267.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Instalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Noroeste', s.id, 315.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout AC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Nordeste', s.id, 261.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout AC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Centro Ocidental', s.id, 260.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout AC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Centro Oriental', s.id, 302.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout AC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Metropolitana', s.id, 143.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout AC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Sudeste', s.id, 307.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout AC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Sudoeste', s.id, 298.21 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout AC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Noroeste', s.id, 352.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout ABC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Nordeste', s.id, 298.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout ABC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Centro Ocidental', s.id, 298.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout ABC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Centro Oriental', s.id, 339.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout ABC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Metropolitana', s.id, 170.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout ABC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Sudeste', s.id, 343.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout ABC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Sudoeste', s.id, 335.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Rollout ABC';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Noroeste', s.id, 248.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Desinstalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Nordeste', s.id, 194.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Desinstalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Centro Ocidental', s.id, 194.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Desinstalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Centro Oriental', s.id, 236.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Desinstalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Metropolitana', s.id, 130.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Desinstalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Sudeste', s.id, 239.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Desinstalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Sudoeste', s.id, 231.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Desinstalação';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Noroeste', s.id, 198.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Local';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Nordeste', s.id, 152.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Local';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Centro Ocidental', s.id, 153.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Local';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Centro Oriental', s.id, 185.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Local';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Metropolitana', s.id, 160.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Local';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Sudeste', s.id, 187.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Local';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Sudoeste', s.id, 188.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Local';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Noroeste', s.id, 354.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Prédio';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Nordeste', s.id, 300.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Prédio';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Centro Ocidental', s.id, 300.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Prédio';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Centro Oriental', s.id, 341.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Prédio';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Metropolitana', s.id, 150.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Prédio';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Sudeste', s.id, 335.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Prédio';
INSERT IGNORE INTO preco_cds (regiao, servico_id, valor) SELECT 'Sudoeste', s.id, 327.00 FROM servico s JOIN empresa e ON e.id = s.empresa_id WHERE e.nome = 'CDS' AND s.nome = 'Mudança de Prédio';

-- WECOM: Realocação e Instalação por serviço; Infraestrutura pelo metro linear
INSERT IGNORE INTO preco_parametro (chave, valor) VALUES
    ('WECOM_REALOCACAO', 4121.86), ('WECOM_INSTALACAO', 970.93), ('WECOM_METRO_LINEAR', 164.18);

-- [/dados-iniciais]
