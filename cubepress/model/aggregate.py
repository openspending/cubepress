import os
from hashlib import sha1

from sqlalchemy.sql.expression import select, func

from cubepress.model.util import make_columns, make_filters


class Aggregate(object):

    def __init__(self, project, filters, drilldowns):
        self.project = project
        self.filters = filters
        self.drilldowns = drilldowns

    def measure_cols(self):
        col = func.count(self.project.table.c._id).label('row_count')
        columns = [col]
        for measure in self.project.model.measures:
            col = func.sum(measure.column).label('%s_sum' % measure.name)
            columns.append(measure.aggregate_column)
        return columns

    def _query(self):
        drilldowns = make_columns(self.project, self.drilldowns)
        columns = self.measure_cols()
        columns.extend(drilldowns)
        return select(columns=columns,
                      whereclause=make_filters(self.project, self.filters),
                      group_by=drilldowns,
                      from_obj=self.project.table)

    def summary(self):
        query = select(columns=self.measure_cols(),
                       whereclause=make_filters(self.project, self.filters),
                       from_obj=self.project.table)
        row = self.project.engine.execute(query).fetchone()
        summary = {
            'row_count': row.row_count,
            'filters': self.filters,
            'drilldowns': self.drilldowns,
            'key': self.key,
            # 'hash': self.hash
        }
        for measure in self.project.model.measures:
            name = measure.aggregate_column.name
            summary[name] = row[name]
        return summary

    def rows(self):
        rp = self.project.engine.execute(self._query())
        while True:
            row = rp.fetchone()
            if row is None:
                return
            yield dict(row.items())

    def get(self):
        return {
            'summary': self.summary(),
            'rows': list(self.rows())
        }

    @property
    def key(self):
        if not hasattr(self, '_key'):
            parts = ['%s=%s' % f for f in self.filters]
            parts.extend(self.drilldowns)
            self._key = '|'.join(sorted(set(parts)))
        return self._key

    @property
    def hash(self):
        return sha1(self.key).hexdigest()

    @property
    def path(self):
        hash = self.hash
        return os.path.join('aggregates', hash[0], hash[1], '%s.json' % hash)
