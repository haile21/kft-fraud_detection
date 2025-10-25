-- Database initialization script
-- This script runs when the PostgreSQL container starts

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE fraud_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'fraud_db')\gexec

-- Connect to the database
\c fraud_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; 

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE fraud_db TO fraud_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fraud_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fraud_user;
