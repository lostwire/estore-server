CREATE_EXTENSION_UUID = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'

CREATE_TABLE_AGGREGATE = """CREATE TABLE IF NOT EXISTS aggregate (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v1(),
    name VARCHAR(100) NOT NULL)"""

CREATE_TABLE_STREAM = """CREATE TABLE IF NOT EXISTS stream (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v1(),
    snapshot INT DEFAULT 0,
    data JSONB NOT NULL DEFAULT '{}')"""

CREATE_TABLE_EVENT = """CREATE TABLE IF NOT EXISTS event (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v1(),
    seq SERIAL,
    stream UUID NOT NULL REFERENCES stream(id),
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    body TEXT NOT NULL,
    headers JSONB NOT NULL DEFAULT '{}',
    UNIQUE(stream, version))"""

CREATE_TABLE_CONSUMER = """CREATE TABLE IF NOT EXISTS consumer (
    id UUID PRIMARY KEY NOT NULL,
    name VARCHAR(100),
    current_sequence INT NOT NULL DEFAULT 0,
    UNIQUE(name))"""

CREATE_TABLE_SUBSCRIPTION = """CREATE TABLE IF NOT EXISTS subscription (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v1(),
    consumer UUID NOT NULL REFERENCES consumer(id),
    routing_key VARCHAR(100) NOT NULL,
    UNIQUE(consumer, routing_key))"""

CREATE_PROCEDURE_ADD_CONSUMER = """CREATE OR REPLACE PROCEDURE add_consumer(id UUID, name VARCHAR(100))
    LANGUAGE SQL
    AS $$
    INSERT INTO consumer (id, name) VALUES (id, name);
    $$;"""

CREATE_PROCEDURE_ADD_SUBSCRIPTION = """CREATE OR REPLACE PROCEDURE add_subscription(id UUID, consumer UUID, routing_key VARCHAR(100))
    LANGUAGE SQL
    AS $$
    INSERT INTO subscription (id, consumer, routing_key) VALUES (id, consumer, routing_key);
    $$;"""

CREATE_PROCEDURE_ADD_EVENT = """CREATE OR REPLACE PROCEDURE add_event(stream UUID, name VARCHAR(100), version INT, body TEXT, headers JSON)
    LANGUAGE SQL
    AS $$
    INSERT INTO event (stream, name, version, body, headers) VALUES (stream, name, version, body, headers);
    $$;"""

SELECT_GET_STREAM_SNAPSHOT = """
    SELECT e.id, e.seq, e.stream, e.created, e.version, e.name, e.body, e.headers
    FROM event AS e
    LEFT JOIN event AS x ON (x.name='Snapshot' AND x.stream=e.stream AND x.version>e.version)
    WHERE e.stream = %s AND x.id IS NULL
    ORDER BY e.version"""

SELECT_GET_STREAM = """
    SELECT id, seq, stream, created, version, name, body, headers
    FROM event WHERE stream = %s ORDER BY version"""


INITIALIZE = [
    CREATE_EXTENSION_UUID,
    CREATE_TABLE_AGGREGATE,
    CREATE_TABLE_STREAM,
    CREATE_TABLE_EVENT,
    CREATE_TABLE_CONSUMER,
    CREATE_TABLE_SUBSCRIPTION,
    CREATE_PROCEDURE_ADD_CONSUMER,
    CREATE_PROCEDURE_ADD_EVENT,
]
