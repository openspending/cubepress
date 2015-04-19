import logging

from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import Table, Column
from sqlalchemy.types import Unicode, Integer, Date, Float

from extract import extract_file

log = logging.getLogger(__name__)

TYPES = {
    'string': Unicode,
    'integer': Integer,
    'float': Float,
    'decimal': Float,  # look away
    'date': Date
}


def generate_table(engine, table_name, fields):
    meta = MetaData()
    meta.bind = engine

    table = Table(table_name, meta)
    id_col = Column('_id', Integer, primary_key=True)
    table.append_column(id_col)

    for spec in fields:
        type_cls = TYPES[spec['type']]
        column = Column(spec['name'], type_cls, nullable=True)
        table.append_column(column)

    table.create(engine)
    log.info("Generated ad-hoc table %s with %d columns.",
             table_name, len(table.columns))
    return table


def load_file(file_name, engine=None, chunk_size=500):
    if engine is None:
        engine = create_engine('sqlite://')

    table = None
    chunk = []
    specs = None
    for i, (table_name, fields, row) in enumerate(extract_file(file_name)):
        if table is None:
            table = generate_table(engine, table_name, fields)
            specs = fields
        chunk.append(row)
        if len(chunk) % chunk_size == 0:
            log.info("Loaded %s rows...", i + 1)
            stmt = table.insert(chunk)
            engine.execute(stmt)
            chunk = []

    if len(chunk):
        stmt = table.insert(chunk)
        engine.execute(stmt)

    log.info("Total: %s rows.", i + 1)
    return engine, table, specs
