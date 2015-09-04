import logging

import click
import yaml

from cubepress.main import process_spec
from cubepress.utils import compute_aggregates



@click.command()
@click.argument('spec', type=click.File('r'))
@click.option('-p', '--datapackage', help='Load datapackage',
              default=None, type=click.Path(exists=True))
@click.option('-d', '--debug', default=False, is_flag=True,
              help='Verbose output for debugging')
def cli(spec, datapackage, debug):
    """ Generate reports based on a particular cube reporting
    specification. """
    if datapackage:
        compute_aggregates(datapackage, spec)
    else:
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        spec_path = spec.name
        spec = yaml.load(spec)
        return process_spec(spec_path, spec)
