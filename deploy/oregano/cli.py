import logging
import click


@click.group()
def cli():
    pass


command = cli.command


def main():
    logging.basicConfig()
    cli()
