import click
import atexit
import asyncio
import estore.app

@click.group()
@click.option('--config', envvar='config', default='./config.ini')
@click.pass_context
def cli(ctx, config):
    """ Estore command line interface """
    loop = asyncio.get_event_loop()
    app = estore.app.init(loop)
    atexit.register(loop.run_until_complete, app.cleanup())
    ctx.obj = app

@cli.command()
@click.pass_context
def initialize(ctx):
    """ Initialize estore application """
    loop = ctx.obj.get_loop()
    results = loop.run_until_complete(ctx.obj.initialize())
    for result in results:
        click.echo(result)

if __name__ == '__main__':
    cli()
