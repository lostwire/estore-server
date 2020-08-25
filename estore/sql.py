import pypika
import pypika.terms
import functools

CREATE_EXTENSION_UUID = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'

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

SELECT_GET_STREAM_SNAPSHOT = """
    SELECT e.id, e.seq, e.stream, e.created, e.version, e.name, e.body, e.headers
    FROM event AS e
    LEFT JOIN event AS x ON (x.name='Snapshot' AND x.stream=e.stream AND x.version>e.version)
    WHERE e.stream = %s AND x.id IS NULL
    ORDER BY e.version"""

SELECT_GET_STREAM = """
    SELECT id, seq, stream, created, version, name, body, headers
    FROM event WHERE stream = %s ORDER BY version"""

def get_stream_snapshot(columns):
    x = pypika.Table('event')
    y = pypika.Table('event')
    query = pypika.Query.from_(x).select(*map(functools.partial(lambda x, y: getattr(x, y), x), columns))
    query = query.left_join(y).on((y.name == "Snapshot") & (x.stream == y.stream) & (x.version>y.version))
    return query.where((x.stream == pypika.terms.PseudoColumn('%s')) & (y.id.isnull())).orderby(x.version)

INITIALIZE = [
    CREATE_EXTENSION_UUID,
    CREATE_TABLE_STREAM,
    CREATE_TABLE_EVENT,
]
