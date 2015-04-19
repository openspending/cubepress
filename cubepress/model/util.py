from normality import slugify
from sqlalchemy.sql.expression import extract


def valid_name(name):
    slug = slugify(name, sep='_')
    if slug != name:
        raise ValueError('Invalid identifier: %s' % name)
    return slug


def resolve_column(model, path):
    parts = path.rsplit(':', 1)
    attribute = model.get_qualified(parts[0])
    # TODO: allow extracting from date objects
    return attribute.column
