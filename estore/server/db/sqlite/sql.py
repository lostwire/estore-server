import pypika
import functools

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
        FOREIGN KEY(stream) REFERENCES stream(id),
        UNIQUE(stream, version))"""

CREATE_TRIGGER_AUTO_SEQUENCE = """
    CREATE TRIGGER IF NOT EXISTS auto_sequence AFTER INSERT ON event
    BEGIN
        UPDATE event SET seq=(SELECT MAX(seq) + 1 FROM event) WHERE id = NEW.id;
    END"""

SELECT_GET_STREAM_SNAPSHOT = """
    SELECT e.id, e.seq, e.stream, e.created, e.version, e.name, e.body, e.headers
    FROM event AS e
    LEFT JOIN event AS x ON (x.name='Snapshot' AND x.stream=e.stream AND x.version>e.version)
    WHERE e.stream = ? AND x.id IS NULL
    ORDER BY e.version"""

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
    CREATE_TABLE_STREAM,
    CREATE_TABLE_EVENT,
    CREATE_TRIGGER_AUTO_SEQUENCE ]
