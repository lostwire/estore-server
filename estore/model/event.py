import uuid
import json
import logging
import asyncio
import operator
import collections

import psycopg2.errors

import estore.sql

logger = logging.getLogger(__name__)

async def iterator(database, query, args, factory):
    async with database.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, (stream_id,))
            keys = list(map(operator.attrgetter('name'), cursor.description))
            async for item in cursor:
                yield dict(zip(keys, map(str,item)))

class Event:
    def __init__(self, loop, database, stream_model, consumer_model):
        self.__loop = loop
        self.__database = database
        self.__stream_model = stream_model
        self.__consumer_model = consumer_model
        self.__consumers = {}
        self.__handlers = []
        self.__counter = {}

    async def __create_stream(self, name):
        pass

    async def add(self, stream_id, name, version, body, headers=None):
        try:
            stream_id = uuid.UUID(stream_id)
        except ValueError:
            raise ValueError("stream_id should be a valid hexadecimal UUID string")
        if not headers:
            headers = {}
        if not 'aggregate' in headers and '.' in name:
            headers['aggregate'], _ = name.split('.', 1)
        headers = json.dumps(headers)
        async with self.__database.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    logger.info("Yes!")
                    await cursor.execute('CALL add_event(%s, %s, %s, %s, %s)', (stream_id, name, version, body, headers))
                except psycopg2.errors.UniqueViolation:
                    pass
                except psycopg2.errors.ForeignKeyViolation:
                    await self.__stream_model.create(stream_id, {})
                    await self.__db.execute('CALL add_event(%s, %s, %s, %s, %s)', (stream_id, name, version, body, headers))
                logger.info(f"Number of consumers: {len(self.__consumers)}")
                for queue in self.__consumers:
                    await self.__consumers[queue]['queue'].put({'one':'stuff'})

    async def __init_consumer(self, consumer_id):
        consumer = self.__consumers[consumer_id]
        logger.info(f"Initializing consumer '{consumer_id}'")
        async with self.__database.acquire() as conn:
            async with conn.cursor() as cursor:
                seq = consumer['seq']
                await cursor.execute("SELECT * FROM event WHERE seq>%s ORDER BY seq", (seq, ))
                keys = list(map(operator.attrgetter('name'), cursor.description))
                while cursor.rowcount:
                    logger.info(f"{cursor.rowcount} events found")
                    async for item in cursor:
                        seq = item[1]
                        await consumer['queue'].put(dict(zip(keys, item)))
                    await cursor.execute("SELECT * FROM event WHERE seq>%s ORDER BY seq", (seq, ))
        await self.__consumer_model.update_current_sequence(consumer_id, seq)

    async def __detach_consumer(self, consumer_id):
        for task in self.__consumers[consumer_id]['tasks']:
            if not task.cancelled():
                task.cancel()
        del self.__consumers[consumer_id]

    async def consume(self, consumer_id, callback):
        if not consumer_id in self.__consumers:
            consumer_data = await self.__consumer_model.get_by_id(consumer_id)
            logger.info(consumer_data)
            self.__consumers[consumer_id] = {
                'queue': asyncio.Queue(),
                'callbacks': [],
                'tasks': [],
                'seq': consumer_data.current_sequence }
            task = asyncio.ensure_future(self.__init_consumer(consumer_id), loop=self.__loop)
            self.__consumers[consumer_id]['tasks'].append(task)
            

        consumer = self.__consumers[consumer_id]
        logger.info(consumer)
        consumer['callbacks'].append(callback)
        queue = consumer['queue']

        logger.info(f"Number of consumers: {len(self.__consumers)}")
        try:
            while True:
                item = await queue.get()
                await callback(item)
        except Exception as e:
            consumer['callbacks'].remove(callback)
            if not len(consumer['callbacks']):
                await self.__detach_consumer(consumer_id)

    async def get_stream(self, stream_id, snapshot=True):
        if snapshot:
            query = estore.sql.SELECT_GET_STREAM_SNAPSHOT
        else:
            query = estore.sql.SELECT_GET_STREAM
        async with self.__database.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (stream_id,))
                keys = list(map(operator.attrgetter('name'), cursor.description))
                async for item in cursor:
                    yield dict(zip(keys, map(str,item)))
