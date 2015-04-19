import logging

from sqlalchemy import MetaData
from sqlalchemy.schema import Table, Column
from sqlalchemy.types import Unicode, Integer, Date, Float

from cubepress.etl.extract import extract_file

log = logging.getLogger(__name__)

TYPES = {
    'string': Unicode,
    'integer': Integer,
    'float': Float,
    'decimal': Float,  # look away
    'date': Date
}


def generate_table(project):
    meta = MetaData()
    meta.bind = project.engine

    table = Table(project.table_name, meta)
    id_col = Column('_id', Integer, primary_key=True)
    table.append_column(id_col)

    # for spec in fields:
    #     type_cls = TYPES[spec['type']]
    #     column = Column(spec['name'], type_cls, nullable=True)
    #     table.append_column(column)

    table.create(project.engine)
    log.info("Generated ad-hoc table %s with %d columns.",
             project.table_name, len(table.columns))
    return table


def load_project(project, chunk_size=500):
    table = None
    chunk = []
    for i, record in enumerate(extract_file(project.data_file)):
        table_name, fields, row = record
        if table is None:
            project.infer_from_data(table_name, fields)
            table = generate_table(project)

        return
        chunk.append(row)
        if len(chunk) % chunk_size == 0:
            log.info("Loaded %s rows...", i + 1)
            stmt = table.insert(chunk)
            project.engine.execute(stmt)
            chunk = []

    if len(chunk):
        stmt = table.insert(chunk)
        project.engine.execute(stmt)

    log.info("Total: %s rows.", i + 1)
