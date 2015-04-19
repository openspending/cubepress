from six import string_types


from cubepress.model.filter import Filter
from cubepress.model.aggregate import Aggregate
from cubepress.model.util import valid_name, distinct_keys


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
        return [(f.path, f.value) for f in self.hierarchy.filters if f.fixed]

    def query_permutations(self):
        ps = [f.path for f in self.hierarchy.filters if not f.fixed]
        ps.extend(self.parent_paths)
        return list(set(ps))

    def generate(self):
        drilldowns = [self.path]
        filters = self.query_filters()
        ps = self.query_permutations()
        for perm_set in distinct_keys(self.hierarchy.project,
                                      paths=ps,
                                      filters=filters):
            pfilters = list(filters)
            pfilters.extend([(p, perm_set[p]) for p in ps])
            aggregate = Aggregate(self.hierarchy.project, pfilters, drilldowns)
            print aggregate.stats()


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
