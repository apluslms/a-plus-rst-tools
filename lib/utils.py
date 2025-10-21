from sphinx.errors import SphinxError

from lib.revealrule import parse_reveal_rule
from directives.abstract_exercise import str_to_bool

def apply_reveal_rules(options, data, source, line):
    if 'show-zero-points-immediately' in options:
        if not 'reveal-submission-feedback' in options:
            raise SphinxError(
                source + ": line " + str(line) +
                "\nOption 'show-zero-points-immediately' requires 'reveal-submission-feedback' to be set!"
            )
    if 'reveal-submission-feedback' in options:
        data['reveal_submission_feedback'] = parse_reveal_rule(
            options['reveal-submission-feedback'],
            source,
            line,
            'reveal-submission-feedback',
        )
        if 'show-zero-points-immediately' in options:
            data['reveal_submission_feedback']['show_zero_points_immediately'] = (
                str_to_bool(options['show-zero-points-immediately'])
            )
    if 'reveal-model-solutions' in options:
        data['reveal_model_solutions'] = parse_reveal_rule(
            options['reveal-model-solutions'],
            source,
            line,
            'reveal-model-solutions',
        )
