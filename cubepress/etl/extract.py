import os
import logging

from normality import slugify
from messytables import any_tableset, type_guess
from messytables import types_processor, headers_guess
from messytables import headers_processor, offset_processor


log = logging.getLogger(__name__)


def column_alias(cell, names):
    """ Generate a normalized version of the column name. """
    column = slugify(cell.column or '', sep='_')
    column = column.strip('_')
    column = 'column' if not len(column) else column
    name, i = column, 2
    # de-dupe: column, column_2, column_3, ...
    while name in names:
        name = '%s_%s' % (name, i)
        i += 1
    return name


def generate_field_spec(row):
    """ Generate a set of metadata for each field/column in
    the data. This is loosely based on jsontableschema. """
    names = set()
    fields = []
    for cell in row:
        name = column_alias(cell, names)
        field = {
            'name': name,
            'title': cell.column,
            'type': unicode(cell.type).lower()
        }
        if hasattr(cell.type, 'format'):
            field['type'] = 'date'
            field['format'] = cell.type.format
        fields.append(field)
    return fields


def parse_table(row_set):
    fields = {}

    offset, headers = headers_guess(row_set.sample)
    row_set.register_processor(headers_processor(headers))
    row_set.register_processor(offset_processor(offset + 1))
    types = type_guess(row_set.sample, strict=True)
    row_set.register_processor(types_processor(types))

    for row in row_set:
        if not len(fields):
            fields = generate_field_spec(row)

        data = {}
        for cell, field in zip(row, fields):
            value = cell.value
            if isinstance(value, basestring) and not len(value.strip()):
                value = None
            data[field['name']] = value

        check_empty = set(data.values())
        if None in check_empty and len(check_empty) == 1:
            continue

        yield fields, data


def extract_file(file_name):
    _, ext = os.path.splitext(file_name)
    with open(file_name, 'rb') as fh:
        table_set = any_tableset(fh, extension=ext.replace('.', ''))
        for row_set in table_set.tables:
            for (fields, row) in parse_table(row_set):
                yield row_set.name, fields, row
            # TODO: log a warning
            return
