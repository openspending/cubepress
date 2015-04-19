import logging

from loader import load_file

logging.basicConfig(level=logging.INFO)

engine, table, spec = load_file('/Users/fl/Code/flatolap/test_data/awards.csv')

print table, spec
