DROP_TABLE_EVENT = 'DROP TABLE IF EXISTS event'
CREATE_TABLE_EVENT = """CREATE TABLE event (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v1(),
    seq SERIAL,
    stream UUID NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    body TEXT NOT NULL,
    headers JSON NOT NULL DEFAULT '{}',
    UNIQUE(stream, version))"""
DROP_TABLE_CONSUMER = 'DROP TABLE IF EXISTS consumer'
CREATE_TABLE_CONSUMER = """CREATE TABLE consumer (
    id UUID PRIMARY KEY NOT NULL,
    name VARCHAR(100),
    UNIQUE(name))"""
DROP_TABLE_SUBSCRIPTION = 'DROP TABLE IF EXISTS subscription'
CREATE_TABLE_SUBSCRIPTION = """CREATE TABLE subscription (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v1(),
    consumer UUID NOT NULL REFERENCES consumer(id),
    routing_key VARCHAR(100) NOT NULL,
    UNIQUE(consumer, routing_key))"""
DROP_PROCEDURE_ADD_CONSUMER = 'DROP PROCEDURE IF EXISTS add_consumer'
CREATE_PROCEDURE_ADD_CONSUMER = """CREATE PROCEDURE add_consumer(id UUID, name VARCHAR(100))
    LANGUAGE SQL
    AS $$
    INSERT INTO consumer (id, name) VALUES (id, name);
    $$;"""
DROP_PROCEDURE_ADD_SUBSCRIPTION = 'DROP PROCEDURE IF EXISTS add_subscription'
CREATE_PROCEDURE_ADD_SUBSCRIPTION = """CREATE PROCEDURE add_subscription(id UUID, consumer UUID, routing_key VARCHAR(100))
    LANGUAGE SQL
    AS $$
    INSERT INTO subscription (id, consumer, routing_key) VALUES (id, consumer, routing_key);
    $$;"""
DROP_PROCEDURE_ADD_EVENT = 'DROP PROCEDURE IF EXISTS add_event'
CREATE_PROCEDURE_ADD_EVENT = """CREATE PROCEDURE add_event(stream UUID, name VARCHAR(100), version INT, body TEXT, headers JSON)
    LANGUAGE SQL
    AS $$
    INSERT INTO event (stream, name, version, body, headers) VALUES (stream, name, version, body, headers);
    $$;"""

QUERIES = [
    DROP_TABLE_EVENT,
    CREATE_TABLE_EVENT,
    DROP_TABLE_SUBSCRIPTION,
    DROP_TABLE_CONSUMER,
    CREATE_TABLE_CONSUMER,
    CREATE_TABLE_SUBSCRIPTION,
    DROP_PROCEDURE_ADD_CONSUMER,
    CREATE_PROCEDURE_ADD_CONSUMER,
    DROP_PROCEDURE_ADD_EVENT,
    CREATE_PROCEDURE_ADD_EVENT,
]
