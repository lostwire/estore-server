import json
import uuid
import functools
import aiohttp.web
import aiohttp_session
import estore.model

class View(object):
    def __init__(self, model):
        self._model = model
    async def login(self, req):
        data = await req.post()
        session = await aiohttp_session.get_session(req)
        if 'id' in session:
            return aiohttp.web.Response(text="Already logged in")
        if 'name' in data:
            id = await self._model.get_id_by_name(data['name'])
        else:
            id = data['id']
        session['id'] = id
        return aiohttp.web.Response(text=session['id'])
    async def logout(self, req):
        session = await aiohttp_session.get_session(req)
        if 'id' in session:
            del session['id']
            return aiohttp.web.Response(text="Logged out")
        return aiohttp.web.Response(text="Already logged out")
    async def register(self, req):
        data = await req.post()
        id = uuid.uuid4()
        await self._model.create_consumer(id, data['name'])
        return aiohttp.web.Response(text=str(id))
    async def test(self, req):
        return aiohttp.web.Response(text='adfsa')
