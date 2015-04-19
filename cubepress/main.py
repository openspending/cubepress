import logging

from cubepress.model import Project
from cubepress.etl import load_project

log = logging.getLogger(__name__)


def process_spec(file_name, spec):
    log.info("Processing project: %s", file_name)
    project = Project(file_name, spec)
    load_project(project)

    print unicode(project)
