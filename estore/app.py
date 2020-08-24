import os
import asyncio
import logging

import configparser

import estore.db
import estore.web
import estore.view
import estore.store
import estore.builtins


logger = logging.getLogger(__name__)


async def init(app):
    config = configparser.ConfigParser()
    config.read(os.environ.get('CONFIG_PATH', './config.ini'))
    estore.view.init(app, estore.store.Store(await estore.db.init(config['general']['db'])))


def create_app():
    estore.builtins.register()
    loop = asyncio.get_event_loop()
    app = estore.web.Application("root", loop=loop)
    app.on_startup.append(init)
    return app
