import os
import logging
import unicodecsv
import jsontableschema
import typecast
from normality import slugify
from jtssql import SchemaTable


log = logging.getLogger(__name__)


def get_schema(project):
    with open(project.data_file, 'r') as fh:
        headers = fh.readline().rstrip('\n').split(',')
        values = unicodecsv.reader(fh)
        schema = jsontableschema.infer(headers, values, row_limit=500)
        for field in schema.get('fields'):
            field['title'] = field['name']
            field['name'] = slugify(field['name'], '_')
        return schema


def cast(field, row):
    return typecast.cast(field.get('type'),
                         row.get(field.get('title')),
                         **field)


def load_rows(project, schema):
    with open(project.data_file, 'r') as fh:
        for i, row in enumerate(unicodecsv.DictReader(fh)):
            yield {f['name']: cast(f, row) for f in schema['fields']}
            if i % 1000 == 0:
                log.info("Loaded %s rows...", i)


def load_project(project):
    table_name, ext = os.path.splitext(os.path.basename(project.data_file))
    table_name = project.config.get('table', table_name)
    schema = get_schema(project)
    project.update_from_data(table_name, schema.get('fields'))
    table = SchemaTable(project.engine, table_name, schema)

    if not table.exists:
        table.create()
        log.info("Generated ad-hoc table %s with %d columns: %r.",
                 table_name, len(table.table.columns),
                 [c.name for c in table.table.columns])
        table.load_iter(load_rows(project, schema))
    else:
        log.info('Data table already exists, not loading data.')
