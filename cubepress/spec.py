from sqlalchemy import create_engine


class Project(object):
    """ A project is the full specification of a given data
    cube and all reports that shall be generated against it.
    """

    def __init__(self, spec_file, spec):
        self.spec_file = spec_file
        self.spec = spec
        self.model = Model(self, spec.get('model', {}))
        self.config = spec.get('config', {})

    @property
    def source_file(self):
        return self.config.get('file')

    @property
    def table_name(self):
        return self.config.get('table')

    @table_name.setter
    def table_name(self, value):
        self.config['table'] = value

    @property
    def engine(self):
        if not hasattr(self, '_engine'):
            uri = self.config.get('database', 'sqlite://')
            self._engine = create_engine(uri)
        return self._engine


class Model(object):
    """ The model defines an abstract representation of the
    data against which reports are specified. Column names
    are mapped to logical dimensions. """

    def __init__(self, project, spec):
        self.project = project
        self.spec = spec
