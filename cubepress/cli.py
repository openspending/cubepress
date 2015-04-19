import logging

import click
import yaml

from cubepress.main import process_spec

# engine, table, spec = load_file('/Users/fl/Code/flatolap/test_data/awards.csv')


@click.command()
@click.argument('spec', type=click.File('rb'))
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
    spec = yaml.load(spec)
    return process_spec(spec_path, spec)
