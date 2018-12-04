import os.path
from docutils.parsers.rst import directives, Directive
from docutils import nodes
from sphinx.errors import SphinxError

import aplus_nodes
import lib.translations as translations
import lib.yaml_writer as yaml_writer
from lib.yaml_writer import ensure_unicode
from directives.abstract_exercise import AbstractExercise

class ExerciseCollection(AbstractExercise):
    has_content = True
    option_spec = {
        'collection_course': directives.unchanged,
        'collection_url': directives.unchanged,
        'collection_category': directives.unchanged,
        'category': directives.unchanged,
        'points-to-pass': directives.nonnegative_int,
        'max_points': directives.nonnegative_int,
    }

    def run(self):

        key, difficulty, points = self.extract_exercise_arguments()
        env = self.state.document.settings.env

        errors = []

        for option in ['collection_category', 'max_points']:
            if option not in self.options:

                # Because warning, error and severe don't make any difference.
                errors.append('Error in {} directive: Missing option {}.'.format(self.name, option))
                #self.severe('Error in {} directive: Missing option {}.'.format(self.name, option))

        if ('collection_course' in self.options) == ('collection_url' in self.options):
            errors.append('Error in {} directive: Must contain either "collection_course" or "collection_url" option.'.format(self.name))

        if ('collection_course' in self.options) and (not ';' in str(self.options.get('collection_course'))):
            # Because warning, error and severe don't make any difference.
            errors.append('Error in {} directive: collection_course must be in format "<course>;<instance>"'.format(self.name))
            #self.reporter.severe('Error in {} directive: collection_course must be in format "<course>;<instance>".'.format(self.name))

        if errors:
            assert False, '\n'.join(errors)

        if 'max_points' in self.options:
            points = int(self.options.get('max_points'))
        else:
            points = 10

        if 'category' in self.options:
            category = str(self.options.get('category'))
        else:
            category = 'Prerequisit'



        name = u"{}_{}".format(env.docname.replace(u'/', u'_'), key)


        node = aplus_nodes.html(u'div',{
            u'class': 'exercisecollection',
            u'data-aplus-exercise': u'yes',
        })



        data = {
            u'key': name,
            u'category': category,
            u'max_points': points,
            u'points_to_pass': self.options.get('points-to-pass'),
            u'collection_course': None,
            u'collection_url': None,
            u'collection_category': self.options.get('collection_category'),
        }
        if 'collection_course' in self.options:
            data[u'collection_course'] = self.options.get('collection_course')
        else:
            data[u'collection_url'] = self.options.get('collection_url')

        node.write_yaml(env, name, data, 'exercisecollection')

        return [node]