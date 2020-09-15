import os
import asyncio
import logging

import configparser

import estore.server.db
import estore.server.web
import estore.server.view
import estore.server.store
import estore.server.builtins


logger = logging.getLogger(__name__)


async def init(app):
    config = configparser.ConfigParser()
    config.read(os.environ.get('CONFIG_PATH', './config.ini'))
    estore.server.view.init(app, estore.server.store.Store(await estore.server.db.init(config['general']['db'], app.loop)))


def create_app():
    estore.server.builtins.register()
    loop = asyncio.get_event_loop()
    app = estore.server.web.Application("root", loop=loop)
    app.on_startup.append(init)
    return app
