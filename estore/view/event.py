import json
import logging
import functools
import asyncio

import aio_pika
import aiohttp.web
import aiohttp_session

logger = logging.getLogger(__name__)
def process_headers(headers):
    output = {}
    for header in headers:
        if header.startswith('X-ES-'):
            output[header.split('X-ES-')[1]] = headers[header]
    return output

def init(app, event_model):
    event = Event(app.loop, event_model)
    app.add_post('/{stream}/{name}', event.add)
    app.add_get('/ws', event.websocket)

class Event(object):
    def __init__(self, loop, event_model):
        self.__loop = loop
        self.__event_model = event_model

    async def add(self, request):
        headers = process_headers(request.headers)
        name = request.match_info['name']
        stream = request.match_info['stream']
        version = headers['Version']
        del headers['Version']
        body = await request.text()
        await self.__event_model.add(stream, name, version, body, headers)
        return aiohttp.web.Response(text='Added')

    async def on_message(self, ws, msg):
        """data = {
                'msg': json.dumps(msg)
        }"""
        logger.info("Message sent %s", msg)
        try:
            keys, values = zip(*msg.items())
            data = dict(zip(keys, map(str, values)))

            await ws.send_json(data)
        except Exception as e:
            logger.info(e)

    async def websocket(self, req):
        ws = aiohttp.web.WebSocketResponse()
        session = await aiohttp_session.get_session(req)
        consumer_id = session['id']
        logger.info("Starting websocket session for")
        await ws.prepare(req)
        task = asyncio.ensure_future(self.__event_model.consume(consumer_id, functools.partial(self.on_message, ws)))
        try:
            async for msg in ws:
                logger.info(msg.type)
                logger.info(msg.data)
        except Exception as e:
            pass
        await ws.close()
        task.cancel()
        logger.info("Closing websocker session for")
        return ws

    def process_event(self, entry):
        entry['id'] = str(entry['id'])
        entry['created'] = str(entry['created'])
        return entry

    async def get_stream(self, req):
        stream = req.match_info['stream']
        output = []
        for entry in await self._model.get_stream(stream):
            output.append(self.process_event(entry))
        return aiohttp.web.json_response(output)
