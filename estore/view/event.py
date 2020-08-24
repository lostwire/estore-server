import json
import uuid
import logging
import functools
import asyncio

import aio_pika
import aiohttp.web
import aiohttp_session

import estore.store

logger = logging.getLogger(__name__)
def process_headers(headers):
    return dict(map(lambda x: (x[0].split('X-ES-')[1], x[1]), filter(lambda x: x[0].startswith('X-ES-'), headers.items())))

def init(app, store):
    event = Event(store, app.loop)
    app.add_post('/{stream}/{name}', event.add)
    app.add_get('/ws', event.websocket)
    app.add_get('/ws/{start}', event.websocket, name='with_start')
    app.add_get('/stream/{stream_id}', event.stream)

async def get_event_from_request(request):
    headers = process_headers(request.headers)
    name = request.match_info['name']
    stream = request.match_info['stream']
    version = headers['Version']
    body = await request.post()
    return estore.store.Event('.'.join((stream, name)), dict(body), headers)


class Event(object):
    def __init__(self, store, loop):
        self.__store = store
        self.__loop = loop

    async def add(self, request):
        event = await get_event_from_request(request)
        await self.__store.append(event)
        return aiohttp.web.Response(text='Added')

    async def __consume(self, ws, start=None):
        async for event in await self.__store[start:]:
            try:
                await ws.send_json(event.dict())
            except Exception:
                raise asyncio.CancelledError()

    async def websocket(self, req):
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(req)
        task = asyncio.ensure_future(self.__consume(ws, req.match_info.get('start', None)), loop=self.__loop)
        try:
            async for msg in ws:
                logger.info(msg.type)
                logger.info(msg.data)
        except Exception as e:
            pass
        await ws.close()
        task.cancel()
        logger.info("Closing websocket session for %s", task)
        return ws

    async def stream(self, req):
        print(await length(self.__store))
        stream = uuid.UUID(req.match_info['stream_id'])
        output = []
        async for item in await self.__store[0:await length(self.__store)]:
            output.append(item.dict())
        return aiohttp.web.json_response(output)
