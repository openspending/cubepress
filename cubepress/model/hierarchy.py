import logging
from six import string_types

from cubepress.model.filter import Filter
from cubepress.model.util import valid_name

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
        return [(f.path, ':', f.value) for f in self.hierarchy.filters
                if f.fixed]

    def query_permutations(self):
        ps = [f.path for f in self.hierarchy.filters if not f.fixed]
        ps.extend(self.parent_paths)
        return list(set(ps))

    def generate(self):
        cube = self.hierarchy.project.cube
        drilldowns = [self.path]
        filters = self.query_filters()
        log.info("Generating aggregates for hierarchy '%s', level %s",
                 self.hierarchy.name, self.index)
        ps = self.query_permutations()

        if not len(ps):
            yield cube.aggregate(drilldowns=drilldowns, cuts=filters)
            return

        page = 0
        while True:
            members = cube.members(','.join(ps), cuts=filters, page=page)
            if not len(members.get('data')):
                return
            count = members.get('total_member_count')
            if count > 10 ** 6:
                log.error('Too many permutations (%s), aborting.', count)
            elif page == 0:
                log.info('%s permutations on level %s', count, self.index)
            page = page + 1

            for member in members.get('data'):
                pfilters = list(filters)
                for name, value in member.items():
                    pfilters.append((name, ':', value))
                yield cube.aggregate(drilldowns=drilldowns, cuts=pfilters)


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
