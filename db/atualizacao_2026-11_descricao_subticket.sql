-- =================================================================================================================
-- Atualização do banco em uso (rodar UMA vez, no Workbench como root, ANTES de trocar o .jar)
-- Branch pendente-e-descricao-subticket. Só acrescenta: nenhum dado existente é alterado ou apagado.
--   1. subticket.descricao: observação opcional de cada subticket (até 250 caracteres).
--   2. demanda.informacoes: Informações adicionais passa de 100 para 250 caracteres.
-- O .jar antigo continua funcionando com o banco já atualizado.
-- Se a linha 1 der "Duplicate column name 'descricao'", a atualização já foi feita: pode ignorar.
-- =================================================================================================================

USE ditic_mudancas_db;

ALTER TABLE subticket ADD COLUMN descricao VARCHAR(250) NULL AFTER metro_linear;

ALTER TABLE demanda MODIFY COLUMN informacoes VARCHAR(250) NULL;

-- conferência: as duas colunas devem aparecer com 250
SELECT TABLE_NAME, COLUMN_NAME, CHARACTER_MAXIMUM_LENGTH
  FROM information_schema.COLUMNS
 WHERE TABLE_SCHEMA = 'ditic_mudancas_db'
   AND ((TABLE_NAME = 'subticket' AND COLUMN_NAME = 'descricao') OR (TABLE_NAME = 'demanda' AND COLUMN_NAME = 'informacoes'));
