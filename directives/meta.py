from docutils import nodes
from docutils.parsers.rst import Directive, directives

from aplus_nodes import aplusmeta


class AplusMeta(Directive):
    ''' Injects document meta data for A+ configuration. '''

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
    #module settings
        'open-time': directives.unchanged,
        'close-time': directives.unchanged,
        'late-time': directives.unchanged,
        'late-penalty': directives.unchanged,
        'audience': directives.unchanged,
        'hidden': directives.flag,
        'points-to-pass': directives.nonnegative_int, # set points to pass for modules
        'introduction': directives.unchanged, # module introduction HTML
    #course settings
        'course-start': directives.unchanged,
        'course-close': directives.unchanged,
        'enrollment-start': directives.unchanged,
        'enrollment-end': directives.unchanged,
        'lifesupport-time': directives.unchanged,
        'archive-time': directives.unchanged,
        'course-late': directives.unchanged,
        'course-late-penalty': directives.unchanged,
        'name': directives.unchanged,
        'view-content-to': directives.unchanged,
        'enrollment-audience': directives.unchanged,
        'index-mode': directives.unchanged,
        'content-numbering': directives.unchanged,
        'module-numbering': directives.unchanged,
        'course-description': directives.unchanged,
        'course-footer': directives.unchanged,
        'numerate-ignoring-modules': directives.unchanged,
    }

    def run(self):
        return [aplusmeta(options=self.options)]
