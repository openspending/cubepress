from cubepress.model.util import distinct_keys


class Filter(object):

    def __init__(self, project, spec):
        self.project = project
        self.spec = spec

    @property
    def path(self):
        return self.spec.get('path')

    @property
    def value(self):
        return self.spec.get('value')

    @property
    def fixed(self):
        return 'value' in self.spec

    @property
    def options(self):
        if self.fixed:
            return [self.value]
        if 'options' not in self.spec:
            # TODO: filters
            options = distinct_keys(self.project, paths=[self.path])
            self.spec['options'] = list(options)
        return self.spec['options']
