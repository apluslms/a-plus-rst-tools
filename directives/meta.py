from docutils import nodes
from docutils.parsers.rst import Directive, directives

from aplus_nodes import aplusmeta


class AplusMeta(Directive):
    ''' Injects document meta data for A+ configuration. '''

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        'open-time': directives.unchanged,
        'close-time': directives.unchanged,
        'late-time': directives.unchanged,
        'late-penalty': directives.unchanged,
        'audience': directives.unchanged,
        'hidden': directives.flag,
        'points-to-pass': directives.nonnegative_int, # set points to pass for modules
    }

    def run(self):
        return [aplusmeta(options=self.options)]
