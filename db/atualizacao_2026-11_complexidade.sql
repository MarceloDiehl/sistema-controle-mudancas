-- =================================================================================================================
-- Atualização do banco em uso (rodar UMA vez, no Workbench como root, ANTES de trocar o .jar)
-- Só acrescenta: nenhum dado existente é alterado ou apagado.
--   demanda.complexidade: Baixa, Normal ou Alta. As demandas que já existem ficam Normal (o padrão da coluna).
-- Rode antes o atualizacao_2026-11_descricao_subticket.sql, se ainda não rodou neste banco.
-- O .jar antigo continua funcionando com o banco já atualizado (a coluna tem valor padrão).
-- Se der "Duplicate column name 'complexidade'", a atualização já foi feita: pode ignorar.
-- =================================================================================================================

USE ditic_mudancas_db;

ALTER TABLE demanda ADD COLUMN complexidade ENUM('BAIXA','NORMAL','ALTA') NOT NULL DEFAULT 'NORMAL' AFTER informacoes;

-- conferência: todas as demandas aparecem como NORMAL
SELECT complexidade, COUNT(*) AS demandas FROM demanda GROUP BY complexidade;
