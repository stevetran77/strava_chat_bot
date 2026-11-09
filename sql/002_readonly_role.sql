-- Read-only role for the chatbot. The password is passed in, never written here:
--   scripts/psql.sh -v ro_password="$CHATBOT_RO_PASSWORD" < sql/002_readonly_role.sql
-- Re-runnable: creates the role if missing, then (re)sets password and grants.
SELECT 'CREATE ROLE chatbot_ro LOGIN' WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'chatbot_ro')\gexec
ALTER ROLE chatbot_ro PASSWORD :'ro_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
ALTER ROLE chatbot_ro SET default_transaction_read_only = on;
ALTER ROLE chatbot_ro SET statement_timeout = '5s';
REVOKE ALL ON SCHEMA public FROM chatbot_ro;
GRANT USAGE ON SCHEMA public TO chatbot_ro;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM chatbot_ro;
GRANT SELECT ON activities, laps, daily_metrics, embeddings, guidance_cards TO chatbot_ro;
