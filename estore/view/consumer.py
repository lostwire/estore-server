import json
import logging
import functools

import aio_pika
import aiohttp.web
import aiohttp_session

logger = logging.getLogger(__name__)

def init(model):
    return View(model)

class View(object):
    def __init__(self, model):
        self._model = model

    async def subscribe(self, req):
        session = await aiohttp_session.get_session(req)
        data = await req.post()
        await self._model.create_subscription(session['id'], data['pattern'])
        logger.info("Subscribed to %s", data['pattern'])
        return aiohttp.web.Response(text='working')
    async def add_event(self, req):
        headers = self.process_headers(req.headers)
        name = req.match_info['name']
        stream = req.match_info['stream']
        version = headers['Version']
        del headers['Version']
        body = await req.text()
        await self._model.add_event(stream, name, version, body, headers)
        return aiohttp.web.Response(text='Added')
    async def on_message(self, ws, msg):
        data = {
            'headers': dict(msg.headers),
            'body': msg.body.decode(),
            'routing_key': msg.routing_key
        }
        logger.info("Message sent %s", data)
        await ws.send_json(data)
    def process_headers(self, headers):
        output = {}
        for header in headers:
            if header.startswith('X-ES-'):
                output[header.split('X-ES-')[1]] = headers[header]
        if 'Content-Type' in headers:
            output['Content-Type'] = headers['Content-Type']
        return output
    async def websocket(self, req):
        ws = aiohttp.web.WebSocketResponse()
        session = await aiohttp_session.get_session(req)
        await ws.prepare(req)
        await self._model.consume(session['id'], functools.partial(self.on_message, ws))
        logger.info("Closing websocker session for %s", session['id'])
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
