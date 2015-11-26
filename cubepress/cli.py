import logging

import click
import json

from cubepress.main import process_spec
from cubepress.utils import compute_aggregates

@click.command()
@click.argument('spec', type=click.File('r'))
@click.option('-d', '--debug', default=False, is_flag=True,
              help='Verbose output for debugging')
def cli(spec, debug):
    """ Generate reports based on a particular cube reporting
    specification. """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    spec_path = spec.name
    spec = json.load(spec)
    return process_spec(spec_path, spec)
