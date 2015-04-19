from sqlalchemy.sql.expression import select, func

from cubepress.model.util import make_columns, make_filters


class Aggregate(object):

    def __init__(self, project, filters, drilldowns):
        self.project = project
        self.filters = filters
        self.drilldowns = drilldowns

    def measure_cols(self):
        col = func.count(self.project.table.c._id).label('_num_cells')
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

    def stats(self):
        query = select(columns=self.measure_cols(),
                       whereclause=make_filters(self.project, self.filters),
                       from_obj=self.project.table)
        row = self.project.engine.execute(query).fetchone()
        stats = {
            '_num_cells': row._num_cells,
            'filters': self.filters,
            'drilldowns': self.drilldowns
        }
        for measure in self.project.model.measures:
            name = measure.aggregate_column.name
            stats[name] = row[name]
        return stats
