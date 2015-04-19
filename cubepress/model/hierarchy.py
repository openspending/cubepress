from six import string_types

from cubepress.model.filter import Filter
from cubepress.model.util import valid_name


class Level(object):

    def __init__(self, hierarchy, parent, spec):
        self.hierarchy = hierarchy
        self.parent = parent
        if isinstance(spec, string_types):
            spec = {'path': spec}
        self.spec = spec

    @property
    def path(self):
        return self.spec.get('path')

    def generate(self):
        print 'Generating %s in %s' % (self.path, self.hierarchy.name)
        drilldowns = []
        filters = []
        permutes = []


class Hierarchy(object):

    def __init__(self, project, name, spec):
        self.project = project
        self.name = valid_name(name)
        self.spec = spec

    @property
    def levels(self):
        msg = 'No levels in hierarchy "%s"' % self.name
        assert 'levels' in self.spec, msg
        assert len(self.spec['levels']), msg

        parent = None
        for spec in self.spec['levels']:
            parent = Level(self, parent, spec)
            yield parent

    @property
    def filters(self):
        for filter in self.project.filters:
            yield filter

        for spec in self.spec.get('filters', []):
            yield Filter(spec)
