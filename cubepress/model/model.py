import logging

from cubepress.model.util import valid_name

log = logging.getLogger(__name__)


class Attribute(object):

    def __init__(self, model, name, spec):
        self.model = model
        self.name = valid_name(name)
        self.spec = spec

    @property
    def column_name(self):
        return self.spec.get('column')

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
        spec['key'] = True
        super(Measure, self).__init__(model, name, spec)


class Dimension(object):

    def __init__(self, model, name, spec):
        self.model = model
        self.name = valid_name(name)
        spec['attributes'] = spec.get('attributes', {})
        self.spec = spec

    @property
    def attributes(self):
        for name, spec in self.spec.get('attributes', {}).items():
            yield Attribute(self.model, name, spec)


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
