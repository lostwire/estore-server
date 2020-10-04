import aiopg
import pypika
import pypika.terms
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

def iterate(database, query, args=None):
    pass

def execute(database, query, args=None):
    pass

async def insert_dict(database, table_name, data):
    pass

async def dummy_item_factory(item):
    return item

async def insert(database, table_name, data):
    columns, values = zip(*data.items())
    query = pypika.Query.into(table_name).columns(*columns).insert(*map(pypika.terms.PseudoColumn, ['%s']*len(values)))
    print(query.get_sql())
    async with database.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query.get_sql(), values)

async def iterator(database, query, params=None, item_factory=dummy_item_factory):
    async with database.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
            async for item in cursor:
                yield await item_factory(item)

async def fetchone(database, query, params=None, item_factory=dummy_item_factory):
    async with database.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
            return await item_factory(await cursor.fetchone())






