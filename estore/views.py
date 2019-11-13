import asyncio
import aiohttp.web
import uuid
import json
import aiohttp_session
import functools
import db
import aio_pika

async def entity_consumer(queue, entity, event):
    if event['name'].startswith(entity):
        await queue.put((event['seq'], event))

async def extract_headers(req):
    output = {}
    for header in req.headers:
        if header.startswith('ES-'):
            output[header.split('-',1)[1]] = req.headers[header]
    return output

async def build_event(req):
    return {
        'stream': req.match_info['stream'],
        'name': req.match_info['name'],
        'body': await req.text(),
        'version': req.headers['Event-Version'],
        'headers': await extract_headers(req)}

class Request(object):
    def __init__(self, req):
        self._req = req

class Handler(object):
    def __init__(self, db):
        self._db = db
        self._consumer = []
        self._queue = {} 

    async def add_event(self, req):
        event = await build_event(req)
        try:
            data = await self._db.add_event(**event)
        except db.EventConflict as e:
            return aiohttp.web.json_response(e.get_events(), status=409)
        event['id'] = str(data['id'])
        event['created'] = str(data['created'])
        event['seq'] = data['seq']
        for consumer in self._consumer:
            await consumer(event)
        return aiohttp.web.Response(text='Working')

    async def get_events(self, req):
        session = await aiohttp_session.get_session(req)
        stream = req.match_info['stream']
        data = await self._db.get_stream(stream)
        output = []
        for row in data:
            output.append(db.to_string(row))
        return aiohttp.web.json_response(output)

    async def subscribe(self, req):
        session = await aiohttp_session.get_session(req)
        if not session['id'] in self._queue:
            self._queue[session['id']] = asyncio.PriorityQueue()
        queue = self._queue[session['id']]
        entity = req.match_info['entity']
        data = req.query
        if 'seq' in data:
            backlog = await self._db.get_events(entity, data['seq'])
            temp_queue = asyncio.PriorityQueue()
            temp_consumer = functools.partial(entity_consumer, temp_queue, entity)
            self._consumer.append(temp_consumer)
            print(len(backlog))
            for event in backlog:
                await queue.put((event['seq'], db.to_string(event)))
            self._consumer.remove(temp_consumer)
        self._consumer.append(functools.partial(entity_consumer, self._queue[session['id']], entity))
        return aiohttp.web.Response(text='Subscribed')

    async def testing(self, req):
        print(req.query)
        return aiohttp.web.Response(text='res')

    async def notify(self, req):
        ws = aiohttp.web.WebSocketResponse()
        session = await aiohttp_session.get_session(req)
        await ws.prepare(req)
        id = session['id']
        if not id in self._queue:
            await ws.send_str("Subscribe to event first")
            await ws.close()
            return ws
        while True:
            msg = await self._queue[id].get()
            await ws.send_json(json.dumps(msg[1]))
        return ws

async def index(loop, req):
    session = await aiohttp_session.get_session(req)
    pika = await aio_pika.connect_robust('amqp://user:pass@rabbitmq/')
    queue_name = 'testowa'
    channel = await pika.channel()
    exchange = await channel.declare_exchange('direct', auto_delete=True)
    queue = await channel.declare_queue(queue_name, auto_delete=True)
    await queue.bind(exchange, queue_name)
    await exchange.publish(
        aio_pika.Message(
        bytes(session['id'], 'utf-8'),
        content_type='text/plain',
        headers={'foo': 'bar'}
        ),
        queue_name 
    )
    message = await queue.get(timeout=5)
    data = message.body.decode()

    await message.ack()
    await queue.unbind(exchange, queue_name)
    await queue.delete()
    await pika.close()

    return aiohttp.web.Response(text=data)
