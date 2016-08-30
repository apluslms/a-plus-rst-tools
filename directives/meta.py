from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive


class aplusmeta(nodes.General, nodes.Element):
    ''' Hidden node that includes meta data. '''

    def __init__(self, options={}):
        self.tagname = 'meta'
        self.options = options
        super().__init__(rawsource='')


def visit_ignore(self, node):
    pass


def depart_ignore(self, node):
    pass


class AplusMeta(Directive):
    ''' Injects document meta data for A+ configuration. '''

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        'open-time': directives.unchanged,
        'close-time': directives.unchanged,
    }

    def run(self):
        return [aplusmeta(options=self.options)]
