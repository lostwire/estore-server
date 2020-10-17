import json
import uuid
import logging

import aiosqlite

import estore.server.db.engine
import estore.server.db.sqlite.sql
import estore.server.db.sqlite.collection

LOGGER = logging.getLogger(__name__)


async def init(config, loop):
    connection = await aiosqlite.connect(config.get('general', 'SQLITE_PATH'), loop=loop)
    engine = SQLite(connection, loop)
    await engine.init()
    return engine


class SQLite(estore.server.db.engine.Engine):
    def __init__(self, connection, loop):
        """ Initialize class
        Arguments:
            connection - sql connection
        """
        self.__loop = loop
        self.__connection = connection

    async def init(self):
        await self.__connection.create_function('DU_STREAM', 1, self.__du_stream)

    def create_collection(self, store):
        collection_factory = estore.server.db.sqlite.collection.CollectionFactory(store, self)
        return collection_factory.events_queue()

    async def __du_stream(self, stream):
        cursor = await self.__connection.execute(
            "SELECT * FROM stream WHERE id = ?", (stream,))
        if not cursor.rowcount > 0:
            cursor.execute("INSERT INTO stream (id, version) VALUES(?,0)", (stream,))
        return stream

    async def iterate(self, query, params=None, item_factory=None):
        cursor = await self.__connection.execute(query, params)
        async for item in cursor:
            yield await item_factory(item)

    async def insert(self, event):
        await self.__connection.execute("""
            INSERT INTO event (id, stream, name, version, body, headers) VALUES(?,?,?,?,?,?)""",
            (str(uuid.uuid4()), str(event.stream), event.name, event.version,
                json.dumps(event.data), json.dumps(event.headers)))
        await self.__connection.commit()

    async def initialize(self):
        cursor = await self.__connection.cursor()
        for query in estore.server.db.sqlite.sql.INITIALIZE:
            await cursor.execute(query)
        await self.__connection.commit()
        await cursor.close()

    async def close(self):
        await self.__connection.close()
