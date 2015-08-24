import csv
import json
from jtssql import SchemaTable
import os
import sqlalchemy
from sqlalchemy import create_engine
import unittest
from datapackage import DataPackage
from utilities import make_sql
from utilities import load_data
from utilities import run_aggregate
from utilities import save_results
from utilities import compute_aggregates

pkgdir = 'tests/fixtures/boost-armenia/'

class TestMethods(unittest.TestCase):
    def test_datapackageload(self):
        package = DataPackage(pkgdir)
        self.assertTrue(package.title == 'Armenia BOOST Government Expenditure Database')

    def test_load_data(self):
        package = DataPackage(pkgdir)
        schema = package.resources[0].schema
        csvpath = pkgdir + package.resources[0].path
        data = [ row for row in csv.DictReader(open(csvpath)) ]
        engine = create_engine('sqlite:///armenia.db')
        table = SchemaTable(engine, 'armenia', schema)
        table.create()
        table.load_iter(data)
        sqla_table = table.table
        res = engine.execute(sqla_table.select())
        self.assertTrue(data == list(res))

    def test_make_sql(self):
        # not sure if this is necessary as jtssql loads data and makes sql
        package = DataPackage(pkgdir)
        self.assertTrue(make_sql(True)

    def test_compute_aggregates(self):
        # compute aggregates using datapackage.json and aggregates.json
        compute_aggregates(pkgdir, pkgdir + "aggregates.json")

        # test aggregates CSV has been created
        self.assertTrue(os.path.isfile(pkgdir + 'aggregates/by-department.csv'))
        
if __name__ == '__main__':
    unittest.main()
