import itertools

from docutils.parsers.rst import Directive, directives
from sphinx.errors import SphinxError


def choice_truefalse(argument):
    """Choice of "true" or "false".
    This is an option conversion function for the option_spec in directives.
    """
    return directives.choice(argument, ('true', 'false', 'True', 'False'))

def str_to_bool(string, error_msg_prefix=''):
    booleans = {
        'true': True,
        'True': True,
        'false': False,
        'False': False,
    }
    try:
        return booleans[string]
    except KeyError:
        raise SphinxError(error_msg_prefix + "{value} is not a boolean".format(value=string))


class AbstractExercise(Directive):
    ''' Abstract exercise directive to extend. '''
    required_arguments = 0
    optional_arguments = 2
    final_argument_whitespace = False

    def extract_exercise_arguments(self):
        key = self.arguments[0] if len(self.arguments) > 0 else 'unknown'
        difficulty, points = self.extract_difficulty_and_points(self.arguments[1] if len(self.arguments) > 1 else None)
        return (key, difficulty, points)

    def extract_difficulty_and_points(self, arg):
        difficulty = None
        points = 0
        if not arg is None:
            for is_number, chars in itertools.groupby(arg, key=lambda a: str.isdigit(str(a))):
                if is_number:
                    points = int(u''.join(chars))
                else:
                    difficulty = u''.join(chars)
        return difficulty, points

    def set_assistant_permissions(self, data):
        if 'allow-assistant-grading' in self.options:
            data['allow_assistant_grading'] = str_to_bool(self.options['allow-assistant-grading'])

        if 'allow-assistant-viewing' in self.options:
            data['allow_assistant_viewing'] = str_to_bool(self.options['allow-assistant-viewing'])
