import os
import yaml

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

    def infer_from_data(self, table_name, fields):
        if self.table_name is None:
            self.config['table'] = table_name
        self.model.match_fields(fields)

    @property
    def data_file(self):
        base_dir = os.path.dirname(os.path.abspath(self.spec_file))
        return os.path.join(base_dir, self.config.get('data'))

    @property
    def table_name(self):
        return self.config.get('table')

    @property
    def table_exists(self):
        if self.table_name is None:
            return False
        return self.engine.has_table(self.table_name)

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


class Attribute(object):

    def __init__(self, model, name, spec):
        self.model = model
        self.name = name
        self.spec = spec

    @property
    def column(self):
        return self.spec.get('column')

    @property
    def type(self):
        return self.spec.get('type')

    @property
    def title(self):
        return self.spec.get('title')

    def matches_field(self, field):
        keys = (field['name'], field['title'])
        if self.column:
            return self.column in keys
        if self.name in keys:
            return True
        return self.title in keys

    def update_from_field(self, field):
        if not self.column:
            self.spec['column'] = field['name']
        if not self.type:
            self.spec['type'] = field['type']
        if not self.title:
            self.spec['title'] = field['title']


class Measure(Attribute):

    def __init__(self, model, name, spec):
        spec['key'] = True
        super(Measure, self).__init__(model, name, spec)


class Dimension(object):

    def __init__(self, model, name, spec):
        self.model = model
        self.name = name
        spec['attributes'] = spec.get('attributes', {})
        self.spec = spec

    @property
    def attributes(self):
        for name, spec in self.spec.get('attributes', {}).items():
            yield Attribute(self, name, spec)


class Model(object):
    """ The model defines an abstract representation of the
    data against which reports are specified. Column names
    are mapped to logical dimensions. """

    def __init__(self, project, spec):
        self.project = project
        spec['measures'] = spec.get('measures', {})
        spec['dimensions'] = spec.get('dimensions', {})
        self.spec = spec

    @property
    def measures(self):
        for name, spec in self.spec.get('measures', {}).items():
            yield Measure(self, name, spec)

    @property
    def dimensions(self):
        for name, spec in self.spec.get('dimensions', {}).items():
            yield Dimension(self, name, spec)

    @property
    def attributes(self):
        for measure in self.measures:
            yield measure
        for dimension in self.dimensions:
            for attribute in dimension.attributes:
                yield attribute

    def match_fields(self, fields):
        for field in fields:
            in_model = False
            for attribute in self.attributes:
                if attribute.matches_field(field):
                    in_model = True
                    attribute.update_from_field(field)

            if not in_model and \
                    field['name'] not in self.spec['dimensions']:
                self.spec['dimensions'][field['name']] = {
                    'title': field['title'],
                    'attributes': {
                        field['name']: {
                            'column': field['name'],
                            'title': field['title'],
                            'type': field['type'],
                            'key': True
                        }
                    }
                }
