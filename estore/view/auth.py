""" View handling user account related activities
"""

import logging

import aiohttp.web
import aiohttp_session

logger = logging.getLogger(__name__)

def init(app, consumer_model):
    view = View(consumer_model)
    app.add_post('/login', view.login)
    app.add_get('/logout', view.logout)
    app.add_post('/register', view.register)
    app.add_get('/whoami', view.whoami)


class View(object):
    def __init__(self, consumer_model):
        self.__consumer_model = consumer_model

    async def login(self, request):
        data = await request.post()
        session = await aiohttp_session.get_session(request)
        if 'id' in session:
            return aiohttp.web.Response(text="Already logged in")
        if 'name' in data:
            consumer = await self.__consumer_model.get_by_name(data['name'])
        else:
            consumer = await self.__consumer_model.get_by_id(data['id'])
        session['id'] = str(consumer.id)
        logger.info(f"User {consumer.name} logged in")
        return aiohttp.web.Response(text=str(consumer.id))

    async def logout(self, req):
        session = await aiohttp_session.get_session(req)
        if 'id' in session:
            del session['id']
            return aiohttp.web.Response(text="Logged out")
        return aiohttp.web.Response(text="Already logged out")

    async def register(self, req):
        data = await req.post()
        print(await req.text())
        await self.__consumer_model.register(data['name'])
        return aiohttp.web.Response(text=str(id))

    async def whoami(self, request):
        session = await aiohttp_session.get_session(request)
        consumer_id = session['id']
        consumer = await self.__consumer_model.get_by_id(consumer_id)
        return aiohttp.web.Response(text=consumer.name)
