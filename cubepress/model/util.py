# coding: utf-8
from normality import slugify


def valid_name(name):
    slug = slugify(name, sep='_')
    if slug != name or slug == 'row_count':
        raise ValueError('Invalid identifier: %s' % name)
    return slug

def translate_fdp(fmodel):
    bmodel = {
        "measures": {},
        "dimensions": {}
    }
    for measure in fmodel.get("measures", {}):
        bmodel["measures"][measure["name"]] = {
            "column": measure["source"]
        }
    for dimension in fmodel.get("dimensions", {}):
        bmodel["dimensions"][dimension["name"]] = {"attributes": {}}
        for field in dimension["fields"]:
            field["column"] = field["source"]
            field.pop("source")
            fname = field["name"]
            field.pop("name")
            bmodel["dimensions"][dimension["name"]]["attributes"][fname] = field
    return bmodel
