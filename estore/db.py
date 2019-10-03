import json
import uuid
import aiopg
import functools
import psycopg2.extras

def to_string(event):
    return {
        'id': str(event['id']),
        'stream': str(event['stream']),
        'seq': event['seq'],
        'created': str(event['created']),
        'version': event['version'],
        'name': event['name'],
        'body': event['body'],
        'headers': event['headers']}

class EventConflict(Exception):
    def __init__(self, events):
        self._events = events
    def get_events(self):
        return self._events

async def close_pg(db, wg=None):
    db.close()
    await db.wait_closed()

class Wrapper(object):
    def __init__(self, db):
        self._db = db
    def get_db(self):
        return self._db
    async def fetch_all(self, query, args):
        with (await self._db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)) as cur:
            await cur.execute(query, args)
            if cur.rowcount:
                return await cur.fetchall()
    async def fetch_one(self, query, args):
        with (await self._db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)) as cur:
            await cur.execute(query, args)
            return await cur.fetchone()
    async def execute(self, query, args):
        with (await self._db.cursor()) as cur:
            await cur.execute(query, args)


class DB(object):
    def __init__(self, db):
        self.__db = db
    async def add_event(self, stream, version, name, body, headers):
        id = str(uuid.uuid4())
        with (await self.__db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)) as cur:
            await cur.execute('SELECT * FROM event WHERE stream = %s AND version >= %s', [stream, version])
            if cur.rowcount:
                events = []
                for row in await cur.fetchall():
                    events.append(to_string(row))
                print(cur.rowcount)
                print(version)
                print(events)
                raise EventConflict(events)
            await cur.execute('CALL add_event (%s, %s,%s,%s,%s,%s)', [id, stream, version, name, body, json.dumps(headers)])
            await cur.execute('SELECT id, seq, created FROM event WHERE id = %s', [id])
            return await cur.fetchone()

    async def get_events(self, entity, seq=None):
        query = 'SELECT * FROM event WHERE {} ORDER BY seq'
        with (await self.__db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)) as cur:
            where = 'name LIKE CONCAT(%s,\'%%\')'
            params = [entity]
            if seq:
                where = where + ' AND seq >= %s'
                params.append(seq)
            await cur.execute(query.format(where), params)
            return await cur.fetchall()

    async def get_stream(self, stream, seq=None):
        query = 'SELECT * FROM event WHERE {} ORDER BY seq'
        with (await self.__db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)) as cur:
            where = 'stream=%s'
            params = [stream]
            if seq:
                where = where + ' AND seq >= %s'
                params.append(seq)
            await cur.execute(query.format(where), params)
            return await cur.fetchall()

async def init(user, database, host, password):
    return await aiopg.create_pool(user=user, database=database, host=host, password=password)
