-- Enable UUID helpers
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- === USERS =========================================================
CREATE TABLE users (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       TEXT NOT NULL,
    email      TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO users(name, email) VALUES ('admin', 'admin@admin.com');

-- === CHAT SESSIONS ================================================
CREATE TABLE chat_sessions (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id)
                ON DELETE CASCADE,
	title		TEXT NOT NULL,
    is_visible BOOLEAN DEFAULT True,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at   TIMESTAMPTZ
);

INSERT INTO chat_sessions(user_id, title, is_visible) VALUES ((SELECT id FROM users WHERE email = 'admin@admin.com' LIMIT 1), 'The files are uploaded by system', False);
CREATE INDEX ON chat_sessions(user_id, is_visible, started_at DESC);

-- === MESSAGES ======================================================
CREATE TABLE messages (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id)
                ON DELETE CASCADE,
    question   TEXT NOT NULL,
	answer     TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    edited_at  TIMESTAMPTZ
);

CREATE INDEX ON messages(session_id, created_at);

-- === UPLOADED FILES ======================================================
CREATE TABLE uploaded_files (
    id         SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES chat_sessions(id)
                ON DELETE CASCADE,
    name   TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    edited_at  TIMESTAMPTZ
);

CREATE INDEX ON uploaded_files(session_id, created_at);

