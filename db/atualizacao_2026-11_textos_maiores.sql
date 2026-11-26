-- =================================================================================================================
-- Atualização do banco em uso (rodar no Workbench como root, ANTES de trocar o .jar)
-- Só aumenta o tamanho de dois campos de texto: nenhum dado existente é alterado ou apagado.
--   1. subticket.descricao: a descrição do subticket passa de 250 para 1000 caracteres.
--   2. historico.texto: passa de 500 para 1200 caracteres (o histórico guarda a descrição inteira do subticket).
-- Ordem: depois do atualizacao_2026-11_descricao_subticket.sql (e do atualizacao_2026-11_complexidade.sql).
-- Pode rodar mais de uma vez sem problema. O .jar antigo continua funcionando com o banco atualizado.
-- =================================================================================================================

USE ditic_mudancas_db;

ALTER TABLE subticket MODIFY COLUMN descricao VARCHAR(1000) NULL;

ALTER TABLE historico MODIFY COLUMN texto VARCHAR(1200) NOT NULL;

-- conferência: subticket.descricao com 1000 e historico.texto com 1200
SELECT TABLE_NAME, COLUMN_NAME, CHARACTER_MAXIMUM_LENGTH
  FROM information_schema.COLUMNS
 WHERE TABLE_SCHEMA = 'ditic_mudancas_db'
   AND ((TABLE_NAME = 'subticket' AND COLUMN_NAME = 'descricao') OR (TABLE_NAME = 'historico' AND COLUMN_NAME = 'texto'));
