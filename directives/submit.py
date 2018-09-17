# -*- coding: utf-8 -*-
'''
Directive that places exercise submission forms.
'''
import os.path
from docutils.parsers.rst import directives
from docutils import nodes
from sphinx.errors import SphinxError

import aplus_nodes
import lib.translations as translations
import lib.yaml_writer as yaml_writer
from lib.yaml_writer import ensure_unicode
from directives.abstract_exercise import AbstractExercise


class SubmitForm(AbstractExercise):
    has_content = False
    option_spec = {
        'class' : directives.class_option,
        'quiz': directives.flag,
        'ajax': directives.flag,
        'submissions': directives.nonnegative_int,
        'points-to-pass': directives.nonnegative_int,
        'config': directives.unchanged,
        'url': directives.unchanged,
        'title': directives.unchanged,
        'lti': directives.unchanged,
        'lti_context_id': directives.unchanged,
        'lti_resource_link_id': directives.unchanged,
        'radar_tokenizer': directives.unchanged,
        'radar_minimum_match_tokens': directives.unchanged,
        'category': directives.unchanged,
    }

    def run(self):
        key, difficulty, points = self.extract_exercise_arguments()

        env = self.state.document.settings.env
        name = u"{}_{}".format(env.docname.replace(u'/', u'_'), key)
        override = env.config.override

        classes = [u'exercise']
        if 'class' in self.options:
            classes.extend(self.options['class'])
        if difficulty:
            classes.append(u'difficulty-' + difficulty)

        # Add document nodes.
        args = {
            u'class': u' '.join(classes),
            u'data-aplus-exercise': u'yes',
        }
        if 'quiz' in self.options:
            args[u'data-aplus-quiz'] = u'yes'
        if 'ajax' in self.options:
            args[u'data-aplus-ajax'] = u'yes'
        node = aplus_nodes.html(u'div', args)
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
                data[u'url'] = ensure_unicode(self.options['url'])
            if 'lti' in self.options:
                data.update({
                    u'lti': ensure_unicode(self.options['lti']),
                    u'lti_context_id': ensure_unicode(self.options.get('lti_context_id', u'')),
                    u'lti_resource_link_id': ensure_unicode(self.options.get('lti_resource_link_id', u'')),
                })
            config_title = None

        config_title = self.options.get('title', config_title)
        if "radar_tokenizer" in self.options or "radar_minimum_match_tokens" in self.options:
            data[u'radar_info'] = {
                u'tokenizer': self.options.get("radar_tokenizer"),
                u'minimum_match_tokens': self.options.get("radar_minimum_match_tokens"),
            }

        category = u'submit'
        data.update({
            u'key': name,
            u'title': env.config.submit_title.format(
                key_title=key_title, config_title=config_title
            ),
            u'category': u'submit',
            u'scale_points': points,
            u'difficulty': difficulty or '',
            u'max_submissions': self.options.get('submissions', data.get('max_submissions', env.config.program_default_submissions)),
            u'min_group_size': data.get('min_group_size', env.config.default_min_group_size),
            u'max_group_size': data.get('max_group_size', env.config.default_max_group_size),
            u'points_to_pass': self.options.get('points-to-pass', data.get('points_to_pass', 0)),
        })
        if category in override:
            data.update(override[category])
            if 'url' in data:
                data['url'] = data['url'].format(key=name)

        if 'category' in self.options:
            data['category'] = str(self.options['category'])

        node.write_yaml(env, name, data, 'exercise')

        return [node]
