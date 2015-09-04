import nose
import unittest
import os
from sqlalchemy import create_engine,func
from cubepress.utils import compute_aggregates,load_data,save_res

pkgdir = 'tests/fixtures/dataset-cra/'

class TestMethods(unittest.TestCase):
    def test_compute_aggregates(self):
        # compute aggregates using datapackage.json and aggregates.json
        compute_aggregates(pkgdir, open(pkgdir + "aggregates.json"))
        agg1 = pkgdir + 'aggregates/by-cofog1-then-department-2010.csv'
        agg2 = pkgdir + 'aggregates/by-department-2010.csv'
        # test that aggregate CSV has been created
        self.assertTrue(os.path.isfile(agg1) and os.path.isfile(agg2))

    def test_load_data(self):
        # there should be 364 entries for dept_code Dept020
        engine = create_engine('sqlite:///:memory:')
        load_data(pkgdir,engine)
        result = engine.execute("select count(*) as c from 'table' where dept_code = 'Dept020'")
        rp = result.fetchone()
        self.assertTrue(rp.c == 364)

    def test_save_res(self):
        engine = create_engine('sqlite:///:memory:')
        load_data(pkgdir,engine)
        result = engine.execute("select count(*) as c from 'table' where dept_code = 'Dept020'")
        save_res("tests/fixtures/test",result,"csv")
        self.assertTrue(os.path.isfile("tests/fixtures/test.csv"))

if __name__ == '__main__':
    unittest.main()
