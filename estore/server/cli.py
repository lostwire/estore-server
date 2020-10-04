import click
import asyncio
import configparser

import estore.server.app

class View:
    def __init__(self, store, loop):
        self.__store = store
        self.__loop = loop

    def initialize(self):
        self.__loop.run_until_complete(self.__store.initialize())

@click.group()
@click.option('--config', envvar='config', default='./config.ini', type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config):
    """ Estore command line interface """
    config_ = configparser.ConfigParser()
    config_.read(config)
    loop = asyncio.get_event_loop()
    store = loop.run_until_complete(estore.server.app.initialize_store(config, loop))
    ctx.obj = View(store, loop)

@cli.command()
@click.pass_context
def initialize(ctx):
    """ Initialize estore application """
    ctx.obj.initialize()


if __name__ == '__main__':
    cli()
