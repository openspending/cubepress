import logging

from sqlalchemy import MetaData
from sqlalchemy.schema import Table, Column
from sqlalchemy.types import Unicode, BigInteger, Integer, Date, Float, Boolean

from cubepress.etl.extract import extract_file
from cubepress.etl.convert import convert_row

log = logging.getLogger(__name__)

TYPES = {
    'string': Unicode,
    'integer': BigInteger,
    'bool': Boolean,
    'float': Float,
    'decimal': Float,  # look away
    'date': Date
}


def generate_table(project, table_name, fields):
    project.update_from_data(table_name, fields)
    meta = MetaData()
    meta.bind = project.engine

    if project.engine.has_table(project.table_name):
        log.info('Data table already exists, not loading data.')
        return False

    table = Table(project.table_name, meta)
    id_col = Column('_id', Integer, primary_key=True)
    table.append_column(id_col)

    seen = set()
    for concept in project.model.concepts:
        if concept.column_name not in seen:
            seen.add(concept.column_name)
            for field in fields:
                if field.get('name') != concept.column_name:
                    continue
                type_cls = TYPES[field.get('type')]
                column = Column(concept.column_name, type_cls, nullable=True)
                table.append_column(column)

    table.create(project.engine)
    log.info("Generated ad-hoc table %s with %d columns: %r.",
             project.table_name, len(table.columns),
             [c.name for c in table.columns])
    project._table = table
    return table


# def field_attributes(project, fields):
#     mapping = {}
#     for field in fields:
#         for attr in project.model.attributes:
#             if attr.column_name == field['name']:
#                 mapping[field['name']] = attr
#     return mapping


def load_project(project, chunk_size=500):
    table = None
    # attributes = {}
    chunk = []
    for i, record in enumerate(extract_file(project.data_file)):
        line = i + 1
        table_name, fields, row = record
        if table is None:
            table = generate_table(project, table_name, fields)
            if table is False:
                return
            # attributes = field_attributes(project, fields)

        chunk.append(convert_row(fields, row, line))
        if len(chunk) % chunk_size == 0:
            log.info("Loaded %s rows...", line)
            stmt = table.insert(chunk)
            project.engine.execute(stmt)
            chunk = []

    if len(chunk):
        stmt = table.insert(chunk)
        project.engine.execute(stmt)

    log.info("Total: %s rows.", i + 1)
