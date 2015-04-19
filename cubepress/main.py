import logging

from cubepress.model import Project
from cubepress.etl import load_project
from cubepress.output import write_json

log = logging.getLogger(__name__)


def process_spec(file_name, spec):
    log.info("Processing project: %s", file_name)
    project = Project(file_name, spec)
    load_project(project)

    for hierarchy in project.hierarchies:

        # load all the options:
        for filter in hierarchy.filters:
            assert filter.options is not None

        for level in hierarchy.levels:
            for aggregate in level.generate():
                write_json(project, aggregate.path, aggregate.get())

    cube = dict(project.spec)
    cube.pop('config', None)
    write_json(project, 'cube.json', cube)
