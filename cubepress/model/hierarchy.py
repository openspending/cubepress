import logging
from six import string_types

from cubepress.model.filter import Filter
from cubepress.model.aggregate import Aggregate
from cubepress.model.util import valid_name, distinct_keys, distinct_count
from cubepress.model.util import flatten_row

log = logging.getLogger(__name__)


class Level(object):

    def __init__(self, hierarchy, parent, index, spec):
        self.hierarchy = hierarchy
        self.model = self.hierarchy.project.model
        self.parent = parent
        self.index = index
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
        log.info("Generating aggregates for hierarchy '%s', level %s",
                 self.hierarchy.name, self.index)
        ps = self.query_permutations()

        if not len(ps):
            aggregate = Aggregate(self.hierarchy.project, filters, drilldowns)
            yield aggregate
            return

        count = distinct_count(self.hierarchy.project,
                               paths=ps, filters=filters)
        if count > 10 ** 6:
            log.error('Too many permutations (%s), aborting.', count)
        else:
            log.info('%s permutations on level %s', count, self.index)

        for perm_set in distinct_keys(self.hierarchy.project,
                                      paths=ps, filters=filters):
            pfilters = list(filters)
            pfilters.extend(flatten_row(perm_set).items())
            aggregate = Aggregate(self.hierarchy.project, pfilters, drilldowns)
            yield aggregate


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
        for idx, spec in enumerate(self.spec['levels']):
            parent = Level(self, parent, idx, spec)
            yield parent

    @property
    def filters(self):
        for filter in self.project.filters:
            yield filter

        for spec in self.spec.get('filters', []):
            yield Filter(self.project, spec)
