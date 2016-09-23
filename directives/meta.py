from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive


class meta(nodes.General, nodes.Element):
    ''' Hidden node that includes meta data. '''

    def __init__(self, options={}):
        self.tagname = 'meta'
        self.options = options
        super().__init__(rawsource='')


class Meta(Directive):
    ''' Injects document meta data for A+ configuration. '''

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        'open-time': directives.unchanged,
        'close-time': directives.unchanged,
        'late-close': directives.unchanged,
        'late-penalty': directives.unchanged,
    }

    def run(self):
        return [meta(options=self.options)]
