import pypika
import pypika.terms
import functools

CREATE_EXTENSION_UUID = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'

CREATE_TABLE_SEQUENCE = """CREATE TABLE IF NOT EXISTS sequence (
    index INT NOT NULL)"""

CREATE_FUNCTION_GETNEXTID = """CREATE OR REPLACE FUNCTION get_next_id()
    RETURNS int
    AS $$
    DECLARE
        next_index int;
    BEGIN
        EXECUTE 'UPDATE sequence SET index = index + 1 RETURNING index' INTO next_index;
    RETURN next_index;
    END;
    $$ LANGUAGE 'plpgsql';"""

CREATE_TABLE_EVENT = """CREATE TABLE IF NOT EXISTS event (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v1(),
    seq INT NOT NULL DEFAULT get_next_id(),
    stream UUID NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    body TEXT NOT NULL,
    headers JSONB NOT NULL DEFAULT '{}',
    UNIQUE(stream, version))"""

SELECT_GET_STREAM_SNAPSHOT = """
    SELECT e.id, e.seq, e.stream, e.created, e.version, e.name, e.body, e.headers
    FROM event AS e
    LEFT JOIN event AS x ON (x.name='Snapshot' AND x.stream=e.stream AND x.version>e.version)
    WHERE e.stream = %s AND x.id IS NULL
    ORDER BY e.version"""

SELECT_GET_STREAM = """
    SELECT id, seq, stream, created, version, name, body, headers
    FROM event WHERE stream = %s ORDER BY version"""

CREATE_INDEX_EVENT_IDX = """CREATE INDEX event_idx ON event (stream)"""

def get_stream_snapshot(columns, stream_id):
    x = pypika.Table('event')
    y = pypika.Table('event')
    query = pypika.Query.from_(x).select(*map(functools.partial(lambda x, y: getattr(x, y), x), columns))
    query = query.left_join(y).on((y.name.like("%.Snapshot")) & (x.stream == y.stream) & (x.version<y.version))
    #return query.where((x.stream == pypika.terms.PseudoColumn('%s')) & (y.id.isnull())).orderby(x.version)
    return query.where((x.stream == str(stream_id)) & (y.id.isnull())).orderby(x.version)

def get_stream(columns, stream_id):
    e = pypika.Table('event')
    return pypika.Table(e).select(*columns).where(e.stream == str(stream_id)).orderby(e.version)

INITIALIZE = [
    CREATE_TABLE_SEQUENCE,
    CREATE_FUNCTION_GETNEXTID,
    CREATE_EXTENSION_UUID,
    CREATE_TABLE_EVENT,
    CREATE_INDEX_EVENT_IDX,
]
