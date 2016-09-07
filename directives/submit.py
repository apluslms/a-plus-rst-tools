# -*- coding: utf-8 -*-
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
        'submissions': directives.nonnegative_int,
        'points-to-pass': directives.nonnegative_int,
        'config': directives.unchanged,
        'url': directives.unchanged,
        'title': directives.unchanged,
        'lti': directives.unchanged,
        'lti_context_id': directives.unchanged,
        'lti_resource_link_id': directives.unchanged,
    }

    def run(self):
        key, difficulty, points = self.extract_exercise_arguments()

        env = self.state.document.settings.env
        name = u"{}_{}".format(env.docname.replace(u'/', u'_'), key)

        classes = [u'exercise']
        if 'class' in self.options:
            classes.extend(self.options['class'])

        # Add document nodes.
        node = aplus_nodes.html(u'div', {
            u'class': u' '.join(classes),
            u'data-aplus-exercise': u'yes',
        })
        paragraph = aplus_nodes.html(u'p', {})
        paragraph.append(nodes.Text(translations.get(env, 'submit_placeholder')))
        node.append(paragraph)

        key_title = u"{} {}".format(translations.get(env, 'exercise'), key)

        # Load or create exercise configuration.
        if 'config' in self.options:
            path = os.path.join(env.app.srcdir, self.options['config'])
            if not os.path.exists(path):
                raise SphinxError('Missing config path {}'.format(self.options['config']))
            data = yaml_writer.read(path)
            config_title = data.get(u'title', None)
        else:
            data = { u'_external': True }
            if 'url' in self.options:
                data[u'url'] = self.options['url']
            if 'lti' in self.options:
                data.update({
                    u'lti': self.options['lti'],
                    u'lti_context_id': self.options.get('lti_context_id', u''),
                    u'lti_resource_link_id': self.options.get('lti_resource_link_id', u''),
                })
            config_title = None

        config_title = self.options.get('title', config_title)

        data.update({
            u'key': name,
            u'title': env.config.submit_title.format(
                key_title=key_title, config_title=config_title
            ),
            u'category': u'submit',
            u'scale_points': points,
            u'difficulty': difficulty or '',
            u'max_submissions': self.options.get('submissions', env.config.program_default_submissions),
            u'min_group_size': env.config.default_min_group_size,
            u'max_group_size': env.config.default_max_group_size,
            u'points_to_pass': self.options.get('points-to-pass', 0),
        })
        node.write_yaml(env, name, data, 'exercise')

        return [node]
