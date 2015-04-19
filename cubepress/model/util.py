from normality import slugify


def valid_name(name):
    slug = slugify(name, sep='_')
    if slug != name:
        raise ValueError('Invalid identifier: %s' % name)
    return slug
