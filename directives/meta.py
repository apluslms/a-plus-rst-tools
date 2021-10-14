import re
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.errors import SphinxError

from aplus_nodes import aplusmeta
from lib.revealrule import parse_reveal_rule

class AplusMeta(Directive):
    ''' Injects document meta data for A+ configuration. '''

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        'open-time': directives.unchanged,
        'read-open-time': directives.unchanged,
        'close-time': directives.unchanged,
        'late-time': directives.unchanged,
        'late-penalty': directives.unchanged,
        'audience': directives.unchanged,
        'hidden': directives.flag,
        'points-to-pass': directives.nonnegative_int, # set points to pass for modules
        'introduction': directives.unchanged, # module introduction HTML
        'reveal-submission-feedback': directives.unchanged,
        'reveal-model-solutions': directives.unchanged,
    }

    # Valid date formats are the same as in function parse_date() in
    # toc_config.py:
    # 1. 'YYYY-MM-DD [hh[:mm[:ss]]]'
    # 2. 'DD.MM.YYYY [hh[:mm[:ss]]]'
    date_format = re.compile(
        r"^(\d\d\d\d-\d\d-\d\d|\d\d.\d\d.\d\d\d\d)" # YYYY-MM-DD or DD.MM.YYYY
        "( \d\d(:\d\d(:\d\d)?)?)?$")                # [hh[:mm[:ss]]]

    # Keys in option_spec which require a date format
    date_format_required = {
        'open-time',
        'read-open-time',
        'close-time',
        'late-time',
    }

    # Keys in option_spec which are parsed as reveal rules
    reveal_rules = {
        'reveal-submission-feedback',
        'reveal-model-solutions',
    }

    def run(self):
        env = self.state.document.settings.env
        substitutions = env.config.aplusmeta_substitutions

        # Substitute values of options if a corresponding string is found in
        # the configuration variable aplusmeta_substitutions (set in conf.py).
        # Example:
        #     self.options['open-time'] == 'open01'
        #     aplusmeta_substitutions['open01'] == '2020-01-03 12:00'
        #     # Result
        #     modified_options['open-time'] = '2020-01-03 12:00'
        #
        # See the section "5. Meta (exercise round settings)" in README.md.
        for opt, value in self.options.items():
            old_value = None
            if value in substitutions:
                old_value = value
                self.options[opt] = substitutions[value]
            if opt in AplusMeta.date_format_required:
                self.validate_time(opt, self.options[opt], old_value)
            if opt in AplusMeta.reveal_rules:
                source, line = self.state_machine.get_source_and_line(self.lineno)
                self.options[opt] = parse_reveal_rule(value, source, line, opt)

        return [aplusmeta(options=self.options)]

    def validate_time(self, opt, value, old_value):
        ''' Validates the time of given option-value pair.

        Parameters:
        opt:       key of option (one of self.option_spec)
        value:     value of option (possibly after substitution)
        old_value: value of option before substitution, or None if substitution
                   was not used

        Raises a SphinxError if value is invalid.
        '''
        if AplusMeta.date_format.match(value):
            return

        # Raise a SphinxError with a helpful message.
        source, line = self.state_machine.get_source_and_line(self.lineno)

        msg1 = (
          "{file}, line {line}, directive aplusmeta:\n"
          "option '{name}' has a value '{value}' which is not a date or a substitution.\n"
          "'{value}' should be one of:\n"
          "1. A date in the format 'YYYY-MM-DD [hh[:mm[:ss]]]', e.g., '2020-01-16 16:00'\n"
          "2. A date in the format 'DD.MM.YYYY [hh[:mm[:ss]]]', e.g., '16.01.2020 16:00'\n"
          "3. A substitution text in variable aplusmeta_substitutions in the file\n"
          "   conf.py. See the A-plus RST tools file README.md > Meta (exercise round \n"
          "   settings) for reference."
        )
        msg2 = (
          "{file}, line {line}, directive aplusmeta:\n"
          "option '{name}' has the value '{old_value}' "
          "which substitutes for value '{value}'. This was not recognised as a date.\n"
          "Please check the variable `aplusmeta_substitutions` in the file conf.py.\n"
          "Set the value '{value}' to either:\n"
          "1. A date in the format 'YYYY-MM-DD [hh[:mm[:ss]]]', e.g., '2020-01-16 16:00'\n"
          "2. A date in the format 'DD.MM.YYYY [hh[:mm[:ss]]]', e.g., '16.01.2020 16:00'\n"
        )

        if old_value is None:
            # No substitution
            raise SphinxError(msg1.format(
                file=source,
                line=line,
                name=opt,
                value=value))
        else:
            # Substitution is used
            raise SphinxError(msg2.format(
                file=source,
                line=line,
                name=opt,
                value=value,
                old_value=old_value))
