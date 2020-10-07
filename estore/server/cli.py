import uuid
import click
import logging
import asyncio
import configparser

import estore.base
import estore.server.app

LOGGER = logging.getLogger(__name__)


class View:
    def __init__(self, store, loop):
        self.__store = store
        self.__loop = loop

    def initialize(self):
        LOGGER.info("Initializing")
        return self.__loop.run_until_complete(self.__store.initialize())

    def test(self):
        event = estore.base.Event('sth', uuid.uuid4(), 1, {}, {})
        self.__loop.run_until_complete(self.__store.append(event))

    def close(self):
        return self.__loop.run_until_complete(self.__store.close())



@click.group()
@click.option('--config', envvar='config', default='./config.ini', type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config):
    """ Estore command line interface """
    config_ = configparser.ConfigParser()
    config_.read(config)
    loop = asyncio.get_event_loop()
    store = loop.run_until_complete(estore.server.app.initialize_store(config_, loop))
    ctx.obj = View(store, loop)


@cli.command()
@click.pass_context
def initialize(ctx):
    """ Initialize estore application """
    ctx.obj.initialize()
    ctx.obj.test()
    ctx.obj.close()


if __name__ == '__main__':
    cli()
