import aiopg
import psycopg2.extras

async def init(url, loop):
    conn = await aiopg.create_pool(url, loop=loop)
    #conn = await conn.acquire()
    return conn
    return Database(conn)

class Database:
    def __init__(self, connection):
        self.__connection = connection

    def acquire(self):
        return self.__connection.acquire()

    def cursor(self):
        return self.__connection.cursor()

    async def execute(self, query, *args, **kwargs):
        #conn = await self.__connection.acquire()
        conn = self.__connection
        if 'dict_cursor' in kwargs and kwargs['dict_cursor']:
            cur = await conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cur = await conn.cursor()
        await cur.execute(query, args)
        return cur

    async def close(self, app):
        if not self.__connection.closed:
            self.__connection.close()
            await self.__connection.wait_closed()
