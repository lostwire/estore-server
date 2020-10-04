CREATE_TABLE_STREAM = """
    CREATE TABLE IF NOT EXISTS stream (
        id TEXT NOT NULL PRIMARY KEY,
        version INTEGER NOT NULL
    )"""
CREATE_TABLE_EVENT = """
    CREATE TABLE IF NOT EXISTS event (
        id TEXT NOT NULL PRIMARY KEY,
        seq INTEGER,
        stream TEXT NOT NULL,
        name TEXT NOT NULL,
        version INTEGER NOT NULL,
        body TEXT NOT NULL,
        headers TEXT NOT NULL,
        FOREIGN KEY(stream) REFERENCES stream(id))"""

CREATE_TRIGGER_AUTO_SEQUENCE = """
    CREATE TRIGGER IF NOT EXISTS auto_sequence AFTER INSERT ON event
    BEGIN
        UPDATE event SET seq=(SELECT MAX(seq) + 1 FROM event) WHERE id = NEW.id;
    END"""

INITIALIZE = [
    CREATE_TABLE_STREAM,
    CREATE_TABLE_EVENT,
    CREATE_TRIGGER_AUTO_SEQUENCE ]
