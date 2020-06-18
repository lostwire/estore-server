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
import estore.query


logger = logging.getLogger(__name__)


async def initialize_views(app, models):
    estore.view.init_auth(app, models.consumer)
    estore.view.init_event(app, models.event)


def set_session(app):
    fernet_key = cryptography.fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    secret_key = b'N\x1a\x8cu2\x19\x9f\xf2\xbc]\xach\xd5\x0e\xaf\xf6\xb1R\xe4\xd7\x89Q\xfcv\x93\xaa\xf41\x82/E\xd1'
    aiohttp_session.setup(app, aiohttp_session.cookie_storage.EncryptedCookieStorage(secret_key))


def initialize_queries(db):
    queries = {}
    queries['stream'] = estore.query.Stream(db)
    queries['event'] = estore.query.Event(db)
    Queries = collections.namedtuple('Queries', queries.keys())
    return Queries(*queries.values())

def initialize_models(loop, db, queries):
    models = {}
    models['consumer'] = estore.model.Consumer(db)
    models['stream'] = estore.model.Stream(db)
    models['event'] = estore.model.Event(loop, db, models['stream'], models['consumer'])
    Models = collections.namedtuple('Models', models.keys())
    return Models(*models.values())

async def init(app):
    config = configparser.ConfigParser()
    config.read(os.environ.get('CONFIG_PATH', './config.ini'))
    logger.info(config.sections())
    
    db = await estore.db.init(config['general']['db'], app.loop)
    queries = initialize_queries(db)
    models = initialize_models(app.loop, db, queries)
    set_session(app)
    #app.on_cleanup.append(db.)
    await initialize_views(app, models)

def create_app():
    loop = asyncio.get_event_loop()
    app =  estore.web.Application("root", loop=loop)
    app.on_startup.append(init)
    return app
