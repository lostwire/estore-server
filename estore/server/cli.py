import click
import psycopg2
import configparser

import estore.server.sql

@click.group()
@click.option('--config', envvar='config', default='./config.ini', type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config):
    """ Estore command line interface """
    config_ = configparser.ConfigParser()
    config_.read(config)
    ctx.obj = psycopg2.connect(config_['general']['db'])

@cli.command()
@click.pass_context
def initialize(ctx):
    """ Initialize estore application """
    cursor = ctx.obj.cursor()
    for query in estore.server.sql.INITIALIZE:
        cursor.execute(query)
        click.echo(query)
    ctx.obj.commit()


if __name__ == '__main__':
    cli()
