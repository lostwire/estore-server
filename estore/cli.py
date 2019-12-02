import click
import atexit
import asyncio
import estore.app

@click.group()
@click.option('--config', envvar='config', default='./config.ini')
@click.pass_context
def cli(ctx, config):
    """ Estore command line interface """
    app = estore.app.init()
    atexit.register(app.cleanup)
    ctx.obj = app

@cli.command()
@click.pass_context
def initialize(ctx):
    """ Initialize estore application """
    loop = ctx.obj.get_loop()
    results = ctx.obj.initialize()
    for result in results:
        click.echo(result)

if __name__ == '__main__':
    cli()
