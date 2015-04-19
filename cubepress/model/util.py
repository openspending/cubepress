from normality import slugify

from sqlalchemy import and_
# from sqlalchemy.sql.expression import extract
from sqlalchemy.sql.expression import select


def valid_name(name):
    slug = slugify(name, sep='_')
    if slug != name or slug == 'row_count':
        raise ValueError('Invalid identifier: %s' % name)
    return slug


def resolve_column(model, path):
    parts = path.rsplit(':', 1)
    attribute = model.get_qualified(parts[0])
    # TODO: allow extracting from date objects
    return attribute.column


def make_columns(project, paths):
    cols = []
    for path in paths:
        col = resolve_column(project.model, path)
        col = col.label(path)
        cols.append(col)
    return cols


def make_filters(project, filters):
    filter = and_()
    for path, value in filters:
        col = resolve_column(project.model, path)
        filter = and_(filter, col == value)
    return filter


def distinct_keys(project, paths=[], filters=[]):
    query = select(columns=make_columns(project, paths),
                   whereclause=make_filters(project, filters),
                   from_obj=project.table, distinct=True)
    rp = project.engine.execute(query)
    while True:
        row = rp.fetchone()
        if row is None:
            return
        yield row
