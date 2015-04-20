# coding: utf-8
from normality import slugify
from sqlalchemy import and_
from sqlalchemy.sql.expression import extract
from sqlalchemy.sql.expression import select

LABEL_SEP = u'‽'


def valid_name(name):
    slug = slugify(name, sep='_')
    if slug != name or slug == 'row_count':
        raise ValueError('Invalid identifier: %s' % name)
    return slug


def resolve_columns(model, path):
    part = None
    if ':' in path:
        path, part = path.rsplit(':', 1)
    for attribute in model.match_qualified(path):
        # TODO: allow extracting from date objects
        label = attribute.path.replace('.', LABEL_SEP)
        if part is not None:
            label = '%s:%s' % (label, part)
            column = extract(part, attribute.column)
        else:
            column = attribute.column
        yield attribute, column.label(label)


def resolve_column(model, path):
    columns = list(resolve_columns(model, path))
    for attr, column in columns:
        if len(columns) == 1 or attr and attr.key:
            return column


def make_columns(project, paths):
    cols = []
    for path in paths:
        for attr, col in resolve_columns(project.model, path):
            cols.append(col)
    return cols


def make_filters(project, filters):
    filter = and_()
    for path, value in filters:
        col = resolve_column(project.model, path)
        filter = and_(filter, col == value)
    return filter


def unflatten_row(row, sep=LABEL_SEP):
    out = {}
    for f, v in row.items():
        if sep not in f:
            out[f] = v
        else:
            dim, attr = f.split(sep, 1)
            if dim not in out:
                out[dim] = {}
            out[dim][attr] = v
    return out


def flatten_row(row, sep='.'):
    out = {}
    for k, v in row.items():
        if isinstance(v, dict):
            for ik, iv in v.items():
                ik = '%s%s%s' % (k, sep, ik)
                out[ik] = iv
        else:
            out[k] = v
    return out


def _distinct_query(project, paths, filters):
    return select(columns=make_columns(project, paths),
                  whereclause=make_filters(project, filters),
                  from_obj=project.table, distinct=True)


def distinct_count(project, paths=[], filters=[]):
    query = _distinct_query(project, paths, filters)
    rp = project.engine.execute(query.count())
    return rp.fetchone().values()[0]


def distinct_keys(project, paths=[], filters=[]):
    query = _distinct_query(project, paths, filters)
    rp = project.engine.execute(query)
    while True:
        row = rp.fetchone()
        if row is None:
            return
        yield unflatten_row(row)
