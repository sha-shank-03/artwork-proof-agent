CREATE TABLE IF NOT EXISTS schema_migrations(version integer PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS portfolio_state(id integer PRIMARY KEY CHECK(id=1), version bigint NOT NULL DEFAULT 0, data jsonb NOT NULL);
INSERT INTO portfolio_state(id,data) VALUES(1,'{"invites":{},"sessions":{},"runs":{},"uploads":{},"budgets":{}}') ON CONFLICT DO NOTHING;
INSERT INTO schema_migrations(version) VALUES(1) ON CONFLICT DO NOTHING;
