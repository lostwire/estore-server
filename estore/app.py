import os
import aiopg
import atexit
import base64
import aiohttp.web
import asyncio
import aio_pika
import functools
import estore.db
import estore.sql
import configparser
import aiohttp_session
import aiohttp_session.cookie_storage
import cryptography.fernet

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

    async def initialize(self):
        output = []
        with (await self._db.cursor()) as cur:
            for query in estore.sql.QUERIES:
                await cur.execute(query)
                output.append(query)
        return output

    async def cleanup(self, wg=None):
        if self._db:
            self._db.close()
            await self._db.wait_closed()

    def run(self):
        app = aiohttp.web.Application(loop=self._loop)
        app.on_cleanup.append(self.cleanup)
        fernet_key = cryptography.fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        secret_key = b'N\x1a\x8cu2\x19\x9f\xf2\xbc]\xach\xd5\x0e\xaf\xf6\xb1R\xe4\xd7\x89Q\xfcv\x93\xaa\xf41\x82/E\xd1'
        aiohttp_session.setup(app, aiohttp_session.cookie_storage.EncryptedCookieStorage(secret_key))
        aiohttp.web.run_app(app)
