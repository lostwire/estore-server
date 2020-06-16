import json
import uuid
import operator
import collections

import psycopg2.errors

import estore.errors

def prepare_item(item):
    return collections.namedtuple('Consumer', ('id', 'name'))(*item)

class Event:
    def __init__(self, db):
        self.__db = db

    async def add_event(self, stream, name, version, body, headers=None):
        if not headers:
            headers = {}
        if not 'aggregate' in headers and '.' in name:
            headers['aggregate'], _ = name.split('.', 1)
        headers = json.dumps(headers)
        try:
            await self.__db.execute('CALL add_event(%s, %s, %s, %s, %s)', stream, name, version, body, headers)
        except psycopg2.errors.UniqueViolation:
            pass

    async def consume(self, consumer_id, callback):
        pass

    async def get_stream(self, stream_id, snapshot=True):
        query = """
            SELECT
                e.id,
                e.seq,
                e.stream,
                e.created,
                e.version,
                e.name,
                e.body,
                e.headers
            FROM
                event AS e
            LEFT JOIN event AS x ON (x.name = 'Snapshot' AND x.stream = e.stream AND x.version>e.version)
            WHERE
                e.stream = %s AND x.id IS NULL
            ORDER BY
                e.version"""

        results = await self.__db.execute(query, stream_id)

        keys = list(map(operator.attrgetter('name'), results.description))
        async for item in results:
            yield dict(zip(keys, item))

class Consumer:
    def __init__(self, db):
        self.__db = db

    async def register(self, name):
        consumer_id = uuid.uuid4()
        try:
            await self.__db.execute(
                "INSERT INTO consumer (id, name) VALUES (%s, %s)", consumer_id, name)
        except psycopg2.errors.UniqueViolation:
            raise estore.errors.AlreadyExists(f"User '{name}' already exists")
        return consumer_id

    async def get_by_name(self, name):
        cur = await self.__db.execute("SELECT id, name FROM consumer WHERE name=%s", name)
        if not cur.rowcount:
            raise estore.errors.DoesNotExist(f"User '{name}' does not exist")
        return prepare_item(await cur.fetchone())

    async def get_by_id(self, consumer_id):
        cur = await self.__db.execute("SELECT id, name FROM consumer WHERE id=%s", consumer_id)
        if not cur.rowcount:
            raise estore.errors.DoesNotExist(f"User by id '{consumer_id}' does not exist")
        return prepare_item(await cur.fetchone())

    async def delete(self, consumer_id):
        cur = await self.__db.execute("DELETE FROM consumer WHERE id=%s", consumer_id)
        if not cur.rowcount:
            raise estore.errors.DoesNotExist(f"User by id '{consumer_id}' does not exist")

    async def subscribe(self, consumer_id, pattern):
        subscription_id = uuid.uuid4()
        cur = await self.__db.execute(
            "INSERT INTO subscription (id, name, routing_key) VALUES (%s, %s, %s)",
            subscription_id, consumer_id, pattern)
