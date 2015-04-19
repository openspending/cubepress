# from sqlalchemy import and_
from sqlalchemy.sql.expression import select


def aggregate(model, drilldowns=[], filters=None):
    pass


def distinct_keys(project, keys=[], filters=[]):
    query = select(columns=keys, whereclause=filters,
                   from_obj=project.table, distinct=True)
    rp = project.engine.execute(query)
    while True:
        row = rp.fetchone()
        if row is None:
            return
        yield row
