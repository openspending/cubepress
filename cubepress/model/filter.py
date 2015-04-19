

class Filter(object):

    def __init__(self, spec):
        self.spec = spec

    @property
    def path(self):
        return self.spec.get('path')

    @property
    def value(self):
        return self.spec.get('value')

    @property
    def fixed(self):
        return 'value' not in self.spec

    @property
    def options(self):
        return []
