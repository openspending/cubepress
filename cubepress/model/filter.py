

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
        return []
