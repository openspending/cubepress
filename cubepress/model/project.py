import os
import yaml

from sqlalchemy import MetaData
from sqlalchemy.schema import Table
from sqlalchemy import create_engine

from cubepress.model.model import Model
from cubepress.model.filter import Filter
from cubepress.model.hierarchy import Hierarchy
from cubepress.model.util import valid_name


class Project(object):
    """ A project is the full specification of a given data
    cube and all reports that shall be generated against it.
    """

    def __init__(self, spec_file, spec):
        self.spec_file = spec_file
        self.spec = spec
        self.model = Model(self, spec.get('model', {}))
        self.config = spec.get('config', {})

    def update_from_data(self, table_name, fields):
        if self.table_name is None:
            self.config['table'] = table_name
        self.model.match_fields(fields)

    @property
    def dir(self):
        return os.path.dirname(os.path.abspath(self.spec_file))

    @property
    def data_file(self):
        return os.path.join(self.dir, self.config.get('data'))

    @property
    def path(self):
        return os.path.join(self.dir, self.config.get('path'))

    @property
    def table_name(self):
        return valid_name(self.config.get('table'))

    @property
    def engine(self):
        if not hasattr(self, '_engine'):
            if 'database' not in self.config:
                self.config['database'] = 'sqlite://'
            self._engine = create_engine(self.config.get('database'))
        return self._engine

    @property
    def table(self):
        if not hasattr(self, '_table'):
            meta = MetaData()
            meta.bind = self.engine
            self._table = Table(self.table_name, meta, autoload=True)
        return self._table

    @property
    def filters(self):
        for spec in self.spec.get('filters', []):
            yield Filter(self, spec)

    @property
    def hierarchies(self):
        for name, spec in self.spec.get('hierarchies', {}).items():
            yield Hierarchy(self, name, spec)

    def __unicode__(self):
        return yaml.safe_dump(self.spec, indent=2, canonical=False,
                              default_flow_style=False)
