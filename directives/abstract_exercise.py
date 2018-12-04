import itertools
from docutils.parsers.rst import Directive


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
