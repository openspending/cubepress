import logging

from sqlalchemy.sql.expression import func

from cubepress.model.util import valid_name

log = logging.getLogger(__name__)


class Attribute(object):

    def __init__(self, model, parent, name, spec):
        self.model = model
        self.parent = parent
        self.name = valid_name(name)
        self.spec = spec

    @property
    def column_name(self):
        return self.spec.get('column')

    @property
    def column(self):
        return self.model.project.table.columns[self.column_name]

    @property
    def key(self):
        return self.spec.get('key', False)

    @property
    def path(self):
        if self.parent is None:
            return self.name
        return '%s.%s' % (self.parent.name, self.name)

    @property
    def type(self):
        return self.spec.get('type')

    def matches_field(self, field):
        keys = (field['name'], field['title'])
        if self.column_name:
            return self.column_name in keys
        return self.name in keys

    def update_from_field(self, field):
        self.spec['column'] = field['name']
        if not self.type:
            self.spec['type'] = field['type']


class Measure(Attribute):

    def __init__(self, model, name, spec):
        super(Measure, self).__init__(model, None, name, spec)

    @property
    def aggregate_column(self):
        return func.sum(self.column).label('%s_sum' % self.name)


class Dimension(object):

    def __init__(self, model, name, spec):
        self.model = model
        self.name = valid_name(name)
        spec['attributes'] = spec.get('attributes', {})
        self.spec = spec

    @property
    def attributes(self):
        for name, spec in self.spec.get('attributes', {}).items():
            yield Attribute(self.model, self, name, spec)

    def get_attribute(self, name):
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute

    @property
    def key(self):
        key_attr, attrs = None, list(self.attributes)
        for attribute in attrs:
            if attribute.key:
                if key_attr is not None:
                    raise ValueError("Multiple key attributes in "
                                     "dimension %s" % self.name)
                key_attr = attribute
        if key_attr is None:
            if len(attrs) != 1:
                raise ValueError("Could not determine key attribute "
                                 "for dimension %s" % self.name)
            key_attr = attrs[0]
            key_attr.spec['key'] = True
        return key_attr


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

    def get_dimension(self, name):
        for dimension in self.dimensions:
            if dimension.name == name:
                return dimension

    def match_qualified(self, path):
        for attribute in self.attributes:
            if attribute.path == path:
                return [attribute]
        if '.' not in path:
            dimension = self.get_dimension(path)
            if dimension is not None:
                return dimension.attributes
        raise ValueError('Attribute does not exist: %s' % path)

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
                    if in_model:
                        log.warning("Column %s is used multiple times, make "
                                    "sure the types are identical.",
                                    field['title'])
                    in_model = True
                    attribute.update_from_field(field)

            if not in_model and \
                    field['name'] not in self.spec['dimensions']:
                self.spec['dimensions'][field['name']] = {
                    'attributes': {
                        'label': {
                            'column': field['name'],
                            'type': field['type']
                        }
                    }
                }

        for dimension in self.dimensions:
            assert dimension.key is not None, dimension
