import os
import atexit
import base64
import asyncio
import functools

import aiopg
import aio_pika
import configparser
import aiohttp.web
import aiohttp_session
import aiohttp_session.cookie_storage
import cryptography.fernet

import estore.db
import estore.sql
import estore.route
import estore.model

def init(loop=None):
    if not loop:
        loop = asyncio.get_event_loop()
    app = App(loop)
    loop.run_until_complete(app.init())
    return app

class App(object):
    def __init__(self, loop=None):
        self._loop = loop

    def get_loop(self):
        return self._loop

    async def init(self):
        self._config = configparser.ConfigParser()
        if 'CONFIG' in os.environ:
            self._config.read(os.environ['CONFIG'])
        self._db = await aiopg.create_pool(loop=self._loop,**dict(self._config.items('db')))
        self._pika = await aio_pika.connect_robust(
            self._config.get('general', 'amqp_url'), loop=self._loop)
        self._channel = await self._pika.channel()
        self._exchange = await self._channel.declare_exchange('event', aio_pika.ExchangeType.TOPIC)
        self._model = estore.model.init(self._db, self._pika, self._channel, self._exchange)

    async def run_queries(self, queries):
        output = []
        with (await self._db.cursor()) as cur:
            for query in queries:
                await cur.execute(query)
                output.append(query)
        channel = await self._pika.channel()
        await channel.declare_exchange('event', aio_pika.ExchangeType.TOPIC)
        return output

    def initialize(self):
        return self._loop.run_until_complete(await self.run_queries(estore.sql.INITIALIZE))

    async def reinitialize(self):
        return await self.run_queries(estore.sql.REINITIALIZE)

    def cleanup(self, wg=None):
        if self._db:
            self._db.close()
            self._loop.run_until_complete(self._db.wait_closed())

    def run(self):
        app = aiohttp.web.Application(loop=self._loop)
        app.on_cleanup.append(self.cleanup)
        fernet_key = cryptography.fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        secret_key = b'N\x1a\x8cu2\x19\x9f\xf2\xbc]\xach\xd5\x0e\xaf\xf6\xb1R\xe4\xd7\x89Q\xfcv\x93\xaa\xf41\x82/E\xd1'
        estore.route.attach(app, self._model)
        aiohttp_session.setup(app, aiohttp_session.cookie_storage.EncryptedCookieStorage(secret_key))
        aiohttp.web.run_app(app)
