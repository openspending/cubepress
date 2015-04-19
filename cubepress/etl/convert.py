import logging
from datetime import date

from messytables.types import BoolType
from six import string_types
from dateutil.parser import parse

log = logging.getLogger(__name__)


def convert_unicode(value):
    return unicode(value)


def convert_int(value):
    return int(value)


def convert_float(value):
    return float(value)


def convert_bool(value):
    value = unicode(value).lower().strip()
    if value in BoolType.true_values:
        return True
    if value in BoolType.false_values:
        return False
    raise ValueError('Cannot convert to boolean')


def convert_date(value):
    return parse(unicode(value))


TYPES = {
    'string': (string_types, convert_unicode),
    'integer': (int, convert_int),
    'bool': (bool, convert_bool),
    'float': (float, convert_float),
    'decimal': (float, convert_float),
    'date': (date, convert_date)
}


def convert_row(attributes, row, line_no):
    for column, value in row.items():
        if value is None:
            continue
        attr = attributes.get(column)
        cls, func = TYPES.get(attr.type)
        if isinstance(value, cls):
            continue
        try:
            row[column] = func(value)
        except (ValueError, TypeError, AttributeError), e:
            log.warning("Cannot load value '%s' row %s, type mismatch: %s",
                        value, line_no, e)
            row[column] = None
    return row
