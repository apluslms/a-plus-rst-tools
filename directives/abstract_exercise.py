import itertools
from sphinx.util.compat import Directive


class AbstractExercise(Directive):
    ''' Abstract exercise directive to extend. '''
    required_arguments = 0
    optional_arguments = 2
    final_argument_whitespace = False

    def extract_exercise_arguments(self):
        key = self.arguments[0] if len(self.arguments) > 0 else 'unknown'
        category, points = self.extract_category_and_points(self.arguments[1] if len(self.arguments) > 1 else None)
        return (key, category, points)

    def extract_category_and_points(self, arg):
        category = None
        points = 0
        if not arg is None:
            for is_number, chars in itertools.groupby(arg, key=str.isdigit):
                if is_number:
                    points = int(''.join(chars))
                else:
                    category = ''.join(chars)
        return category, points
