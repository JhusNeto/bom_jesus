-- Script de inicialização do banco de dados
-- Este script é executado automaticamente quando o container PostgreSQL é criado pela primeira vez

-- Criar extensões úteis (se necessário)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- O banco já é criado via variável de ambiente POSTGRES_DB
-- Este script pode ser usado para inicializações adicionais se necessário

SELECT 'Database initialized successfully' AS status;

