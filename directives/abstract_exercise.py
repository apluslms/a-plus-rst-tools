import itertools
from urllib.parse import urlparse

from docutils.parsers.rst import Directive, directives
from sphinx.errors import SphinxError


def file_mapping(argument):
    """
    Converts a comma-separated list of key:value pairs into a dict.
    (Directive option conversion function.)
    """
    args = [arg.split(":") for arg in argument.split(',')]
    for arg in args:
        if not arg or len(arg) > 2:
            raise SphinxError(
                "File mapping must be in the format '<mapping 1>,<mapping 2>,...',"
                " where each <mapping X> is either 'path_on_grader:path_in_repository'"
                " or just 'path' if no renaming is neccessary. E.g."
                " 'extra/grader.txt:configs/repo.txt,files/not-renamed.txt'")

    return dict((arg, arg) if len(arg) == 1 else arg for arg in args)

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
                    points = int(''.join(chars))
                else:
                    difficulty = ''.join(chars)
        return difficulty, points

    def set_assistant_permissions(self, data):
        if 'allow-assistant-grading' in self.options:
            data['allow_assistant_grading'] = str_to_bool(self.options['allow-assistant-grading'])

        if 'allow-assistant-viewing' in self.options:
            data['allow_assistant_viewing'] = str_to_bool(self.options['allow-assistant-viewing'])

class ConfigurableExercise(AbstractExercise):
    option_spec = {
        'configure-url': directives.unchanged,
        'configure-files': file_mapping,
        'category': directives.unchanged,
        'no-configure': directives.flag,
        'no-override': directives.flag,
    }

    def apply_override(self, data, category=None):
        if 'no-override' in self.options:
            return

        if not category:
            if "category" in data:
                category = data["category"]
            elif "category" in self.options:
                category = self.options["category"]

        if not category:
            return

        env = self.state.document.settings.env
        override = env.config.override
        if category in override:
            data.update(override[category])

    def set_url(self, data, name):
        env = self.state.document.settings.env

        if "url" not in data and env.config.default_exercise_url:
            data["url"] = env.config.default_exercise_url

        if "url" in data:
            data["url"] = data["url"].format(key=name)

    def set_configure(self, data, exercise_url, files):
        if 'no-configure' in self.options:
            return

        if "configure-url" in data:
            url = data.pop("configure-url")
        elif "configure-url" in self.options:
            url = self.options["configure-url"]
        else:
            url = self.state.document.settings.env.config.default_configure_url

        if not url:
            return

        if exercise_url:
            url = url.format(**urlparse(exercise_url)._asdict())

        try:
            parsed = urlparse(url)
        except ValueError:
            raise SphinxError(f"Invalid configure url {url} for {data.get('key', data)}")

        if not parsed.scheme or not parsed.netloc:
            raise SphinxError(f"Invalid configure url {url} for {data.get('key', data)}")

        extra_files = {}
        if "configure-files" in data:
            extra_files = data.pop("configure-files")
            if not isinstance(extra_files, dict):
                raise SphinxError(f"configure-files needs to be a dictionary for {data.get('key', data)}")
        if "configure-files" in self.options:
            extra_files = self.options["configure-files"]

        files.update(extra_files)

        data["configure"] = {
            "files": files,
            "url": url,
        }
