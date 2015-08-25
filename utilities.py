import os
import json
import csv
from jtssql import SchemaTable
from sqlalchemy import create_engine
from datapackage import DataPackage

def compute_aggregates(pkgdir,aggregates):
    dpo = DataPackage(pkgdir)
    schema = dpo.resources[0].schema
    csvpath = pkgdir + dpo.resources[0].path
    data = [ row for row in csv.DictReader(open(csvpath)) ]
    engine = create_engine('sqlite:///:memory:')
    table = SchemaTable(engine, ':memory:', schema)
    table.create()
    table.load_iter(data)
    sqla_table = table.table
    aggregates_object = json.load(open(aggregates))
    if not os.path.exists(pkgdir + 'aggregates'):
        os.makedirs(pkgdir + 'aggregates')
    for aggregate in aggregates_object:
        fo = open(pkgdir + 'aggregates/%s.csv' % aggregate['file'], 'w')
        query = aggregate['sql']
        result = engine.execute(query)
        headers = result.keys()
        writer = csv.writer(fo)
        writer.writerows([headers])
        writer.writerows(result)
        
