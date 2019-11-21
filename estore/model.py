import json
import uuid
import logging

import aio_pika
import psycopg2.extras

import estore.db

logger = logging.getLogger(__name__)

def init(db, pika, channel, exchange):
    return Manager(estore.db.Wrapper(db), pika, channel, exchange)

class Manager(object):
    def __init__(self, db, pika, channel, exchange):
        self._db = db
        self._pika = pika
        self._channel = channel
        self._exchange = exchange
    async def create_consumer(self, id, name):
        await self._db.execute('INSERT INTO consumer (id, name) VALUES (%s, %s)', [id, name])
        await self._channel.declare_queue(str(id).encode())
    async def load_consumer(self, id):
        return await self._db.fetch_one('SELECT name FROM consumer WHERE id = %s', [id])
    async def get_id_by_name(self, name):
        output = await self._db.fetch_one('SELECT id FROM consumer WHERE name = %s', [name])
        return output['id']
    async def delete_consumer(self, id):
        await self._db.execute('DELETE FROM consumer WHERE id=%s', [id])
    async def create_subscription(self, consumer, pattern):
        await self._db.execute(
            'INSERT INTO subscription (consumer, routing_key) VALUES (%s, %s)', [consumer, pattern])
        queue = await self._channel.declare_queue(str(consumer).encode())
        await queue.bind(self._exchange, routing_key=pattern)
    async def get_subscriptions(self, consumer):
        return await self._db.fetch_all(
            'SELECT id, routing_key FROM subscription WHERE consumer=%s', [consumer])
    async def consume(self, id, callback):
        queue = await self._channel.declare_queue(str(id).encode())
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    logger.info("Message received %s", message)
                    await callback(message)
    async def add_event(self, stream, name, version, body, headers):
        await self._db.execute(
            'CALL add_event(%s, %s, %s, %s, %s)', [stream, name, version, body, json.dumps(headers)])
        headers['stream'] = stream
        headers['version'] = version
        message = aio_pika.Message(body.encode(), content_type=headers['Content-Type'], headers=headers)
        await self._exchange.publish(message, routing_key=name)
    async def get_stream(self, stream):
        output = await self._db.fetch_all('SELECT id, seq, name, version, body, headers, created FROM event WHERE stream=%s ORDER BY version', [stream])
        if not output:
            output = []
        return output
