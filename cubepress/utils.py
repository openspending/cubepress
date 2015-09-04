import sys
import os
import json
import csv
from jtssql import SchemaTable
from sqlalchemy import create_engine
from datapackage import DataPackage

def load_data(pkgdir,engine):
    dpo = DataPackage(pkgdir)
    schema = dpo.resources[0].schema
    csvpath = pkgdir + dpo.resources[0].path
    data = [ row for row in csv.DictReader(open(csvpath)) ]
    table = SchemaTable(engine, 'table', schema)
    table.create()
    table.load_iter(data)

def run_aggregate(query,engine):
    result = engine.execute(query)
    return result

def save_res(filename,result,fileformat):
    fo = open(filename + "." + fileformat, 'w')
    if fileformat == "csv":
        headers = result.keys()
        writer = csv.writer(fo)
        writer.writerows([headers])
        writer.writerows(result)
    elif fileformat == "json":
        pass

def compute_aggregates(pkgdir,aggregates):
    engine = create_engine('sqlite:///:memory:')
    load_data(pkgdir,engine)
    print(aggregates)
    agg_object = json.load(aggregates)
    agg_dir = pkgdir + 'aggregates'
    if not os.path.exists(agg_dir):
        os.makedirs(agg_dir)
    for aggregate in agg_object:
        agg_file = agg_dir + '/' + aggregate['file']
        res = run_aggregate(aggregate['sql'],engine)
        save_res(agg_file,res,aggregate['format'])

if __name__ == '__main__':
    pkgdir = sys.argv[1]
    print(pkgdir)
    compute_aggregates(pkgdir, open(pkgdir + "aggregates.json"))
