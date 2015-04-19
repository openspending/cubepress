import os
import yaml

from sqlalchemy import create_engine

from cubepress.model.model import Model
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
    def data_file(self):
        base_dir = os.path.dirname(os.path.abspath(self.spec_file))
        return os.path.join(base_dir, self.config.get('data'))

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

    def __unicode__(self):
        return yaml.safe_dump(self.spec, indent=2, canonical=False,
                              default_flow_style=False)
