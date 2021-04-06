import os.path
from docutils.parsers.rst import directives, Directive
from docutils import nodes
from sphinx.errors import SphinxError

import aplus_nodes
import lib.translations as translations
import lib.yaml_writer as yaml_writer
from directives.abstract_exercise import AbstractExercise

class ExerciseCollection(AbstractExercise):
    has_content = True
    required_arguments = 1
    option_spec = {
        'target_url': directives.unchanged,
        'target_category': directives.unchanged,
        'category': directives.unchanged,
        'points-to-pass': directives.nonnegative_int,
        'max_points': directives.nonnegative_int,
    }

    def run(self):

        key, difficulty, points = self.extract_exercise_arguments()
        env = self.state.document.settings.env

        errors = []

        if not 'target_category' in self.options:
            errors.append('Error in {} directive: Missing target_category.'.format(self.name))

        if not 'target_url' in self.options:
            errors.append('Error in {} directive: Missing target_url.'.format(self.name))

        assert not errors, '\n'.join(errors)

        name = "{}_{}".format(env.docname.replace('/', '_'), key)


        node = aplus_nodes.html('div',{
            'class': 'exercisecollection',
            'data-aplus-exercise': 'yes',
        })



        data = {
            'key': name,
            'category': self.options.get('category', 'prerequisit'),
            'max_points': self.options.get('max_points', 10),
            'points_to_pass': self.options.get('points-to-pass', 0),
            'target_url': self.options.get('target_url', None),
            'target_category': self.options.get('target_category', None),
            'title': self.arguments[0]
        }

        node.write_yaml(env, name, data, 'exercisecollection')

        return [node]
