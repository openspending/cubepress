# coding: utf-8
from normality import slugify


def valid_name(name):
    slug = slugify(name, sep='_')
    if slug != name or slug == 'row_count':
        raise ValueError('Invalid identifier: %s' % name)
    return slug
