import json
import uuid
import logging
import functools
import asyncio

import aiohttp.web
import aiohttp_session

import estore.server.store

logger = logging.getLogger(__name__)
def process_headers(headers):
    return dict(map(
        lambda x: (x[0].split('X-ES-')[1], x[1]),
        filter(lambda x: x[0].startswith('X-ES-'), headers.items())))


def init(app, store):
    event = Event(store)
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
    return estore.server.store.Event('.'.join((stream, name)), dict(body), headers)


def get_stream_id_from_request(request):
    return uuid.UUID(request.match_info['stream_id'])


class Event(object):
    def __init__(self, store):
        self.__store = store

    async def add(self, request):
        await self.__store.append(await get_event_from_request(request))
        return aiohttp.web.Response(text='Added')

    async def __consume(self, ws, start=None):
        collection = self.__store

        if start:
            collection = collection[start:]

        async for event in collection:
            try:
                await ws.send_json(event.dict())
            except Exception:
                raise asyncio.CancelledError()

    async def websocket(self, req):
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(req)
        task = asyncio.ensure_future(self.__consume(ws, req.match_info.get('start', None)))
        try:
            async for msg in ws:
                pass
        except Exception as e:
            pass
        await ws.close()
        task.cancel()
        logger.info("Closing websocket session for %s", task)
        return ws

    async def stream(self, request):
        output = []
        async for item in self.__store[get_stream_id_from_request(request)]:
            output.append(item.dict())
        return aiohttp.web.json_response(output)
