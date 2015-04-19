from six import string_types
from sqlalchemy import and_

from cubepress.aggregation import distinct_keys
from cubepress.model.filter import Filter
from cubepress.model.util import valid_name, resolve_column


class Level(object):

    def __init__(self, hierarchy, parent, spec):
        self.hierarchy = hierarchy
        self.model = self.hierarchy.project.model
        self.parent = parent
        if isinstance(spec, string_types):
            spec = {'path': spec}
        self.spec = spec

    @property
    def path(self):
        return self.spec.get('path')

    @property
    def parent_paths(self):
        if self.parent is None:
            return []
        return self.parent.parent_paths + [self.parent.path]

    def query_filters(self):
        filters = and_()
        for filter in self.hierarchy.filters:
            if filter.fixed:
                col = resolve_column(self.model, filter.path)
                filters = filters.and_(col == filter.value)
        return filters

    def query_permutations(self):
        permutations = []
        for filter in self.hierarchy.filters:
            if not filter.fixed:
                permutations.append(filter.path)

        for parent_path in self.parent_paths:
            permutations.append(parent_path)

        return [resolve_column(self.model, p) for p in permutations]

    def generate(self):
        # print 'Generating %s in %s' % (self.path, self.hierarchy.name)
        drilldowns = [resolve_column(self.model, self.path)]
        filters = self.query_filters()
        permutations = self.query_permutations()
        for perm_set in distinct_keys(self.hierarchy.project,
                                      keys=permutations,
                                      filters=filters):
            pfilters = filters
            for perm in permutations:
                pfilters = and_(pfilters, perm == perm_set[perm.name])

            print unicode(pfilters)


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
            yield Filter(self.project, spec)
