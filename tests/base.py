import csv
import json
from jtssql import SchemaTable
import os
import sqlalchemy
from sqlalchemy import create_engine
import unittest
from datapackage import DataPackage
from cubepress.utils import compute_aggregates

pkgdir = 'tests/fixtures/boost-armenia/'

class TestMethods(unittest.TestCase):
    def test_compute_aggregates(self):
        # compute aggregates using datapackage.json and aggregates.json
        compute_aggregates(pkgdir, pkgdir + "aggregates.json")

        # test that at least one aggregate CSV has been created
        self.assertTrue(os.path.isfile(pkgdir + 'aggregates/by-admin2-2006.csv'))
        
if __name__ == '__main__':
    unittest.main()
