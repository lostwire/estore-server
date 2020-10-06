import json
import uuid
import logging

import aiosqlite

import estore.server.db.engine
import estore.server.db.sqlite.sql

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

    def __du_stream(self, stream):
        cursor = self.__conn.cursor()
        cursor.execute("SELECT * FROM stream WHERE id = ?", (stream,))
        print(f"rowcount: {cursor.rowcount}")
        if not cursor.rowcount > 0:
            cursor.execute("INSERT INTO stream (id, version) VALUES(?,0)", (stream,))
        return stream

    async def insert(self, event):
        await self.__connection.execute("""
            INSERT INTO event (id, stream, name, version, body, headers) VALUES(?,?,?,?,?,?)""",
            (str(uuid.uuid4()), str(event.stream), event.name, event.version,
                json.dumps(event.data), json.dumps(event.headers)))
        await self.__connection.commit()

    async def initialize(self):
        LOGGER.info("Running initialize")
        cursor = await self.__connection.cursor()
        for query in estore.server.db.sqlite.sql.INITIALIZE:
            LOGGER.info(f"running {query}")
            await cursor.execute(query)
        await self.__connection.commit()
        await cursor.close()
        LOGGER.info("Changes committed")

    async def stream_snapshot(self):
        pass

    async def close(self):
        LOGGER.info("Dying")
        await self.__connection.close()
