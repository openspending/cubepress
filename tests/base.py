import unittest
import csv
from datapackage import DataPackage

class TestMethods(unittest.TestCase):

  def test_datapackageload(self):
    package = DataPackage('tests/fixtures/boost-armenia/')
    self.assertTrue(package.title == 'Armenia BOOST Government Expenditure Database')

  def test_castrow(self):
    dpdir = 'tests/fixtures/boost-armenia/'
    package = DataPackage(dpdir)
    res = package.resources[0]
    schema = res[u'schema']
    fields = schema[u'fields']
    for resource in package.resources:
      fo = open(dpdir + resource['path'])
      reader = csv.reader(fo)
      row = list(reader)
      castrow(row,fields)
      self.assertTrue(True) # will think more about this
    
if __name__ == '__main__':
    unittest.main()
