import os
import uuid
import base64
import asyncio
import logging
import collections

import aiohttp.web
import configparser
import aiohttp_session
import aiohttp_session.cookie_storage
import cryptography.fernet

import estore.db
import estore.web
import estore.view
import estore.model
import estore.store
import estore.builtins


logger = logging.getLogger(__name__)


async def initialize_views(app, store):
    estore.view.init_event(app, store)


def set_session(app):
    fernet_key = cryptography.fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    secret_key = b'N\x1a\x8cu2\x19\x9f\xf2\xbc]\xach\xd5\x0e\xaf\xf6\xb1R\xe4\xd7\x89Q\xfcv\x93\xaa\xf41\x82/E\xd1'
    aiohttp_session.setup(app, aiohttp_session.cookie_storage.EncryptedCookieStorage(secret_key))


async def init(app):
    config = configparser.ConfigParser()
    config.read(os.environ.get('CONFIG_PATH', './config.ini'))
    logger.info(config.sections())
    store = estore.store.Store(await estore.db.init(config['general']['db'], app.loop))
    store = estore.store.Store(await estore.db.init('postgresql://postgres:example@estore-db/estore', app.loop))
    set_session(app)
    await initialize_views(app, store)


def create_app():
    estore.builtins.register()
    loop = asyncio.get_event_loop()
    app = estore.web.Application("root", loop=loop)
    app.on_startup.append(init)
    return app
