'''
Directive that places exercise submission forms.
'''
import os.path
from docutils.parsers.rst import directives
from docutils import nodes
from sphinx.errors import SphinxError

import aplus_nodes
import translations
import yaml_writer
from directives.abstract_exercise import AbstractExercise


class SubmitForm(AbstractExercise):
    has_content = False
    option_spec = {
        'class' : directives.class_option,
        'ajax': directives.flag,
        'submissions': directives.nonnegative_int,
        'points-to-pass': directives.nonnegative_int,
        'config': directives.unchanged,
        'url': directives.unchanged,
        'lti': directives.unchanged,
        'lti_context_id': directives.unchanged,
        'lti_resource_link_id': directives.unchanged,
    }

    def run(self):
        key, category, points = self.extract_exercise_arguments()

        env = self.state.document.settings.env
        # name = env.docname.replace('/', '_') + '_' + key
        name = key

        classes = ['exercise']
        if 'class' in self.options:
            classes.extend(self.options['class'])

        # Add document nodes.
        args = {
          'class': ' '.join(classes),
          'data-aplus-exercise': 'yes',
        }
        if 'ajax' in self.options:
            args[u'data-aplus-ajax'] = u'yes'
        node = aplus_nodes.html('div', args)
        paragraph = aplus_nodes.html('p', {})
        paragraph.append(nodes.Text(translations.get(env, 'submit_placeholder')))
        node.append(paragraph)

        # Load or create exercise configuration.
        if 'config' in self.options:
            path = os.path.join(env.app.srcdir, self.options['config'])
            if not os.path.exists(path):
                raise SphinxError('Missing config path {}'.format(self.options['config']))
            data = yaml_writer.read(path)
        else:
            data = {
                '_external': True,
                'title': translations.get(env, 'exercise') + ' ' + key,
            }
            if 'url' in self.options:
                data['url'] = self.options['url']
            if 'lti' in self.options:
                data.update({
                    'lti': self.options['lti'],
                    'lti_context_id': self.options.get('lti_context_id', ''),
                    'lti_resource_link_id': self.options.get('lti_resource_link_id', ''),
                })

        data.update({
            'key': name,
            'category': category or 'exercise',
            'scale_points': points,
            'max_submissions': self.options.get('submissions', env.config.program_default_submissions),
            'points_to_pass': self.options.get('points-to-pass', 0),
        })
        node.write_yaml(env, name, data, 'exercise')

        return [node]
