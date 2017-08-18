# -*- coding: utf-8 -*-
'''
Directive that places active element inputs.
'''
import os.path
from docutils.parsers.rst import directives
from docutils import nodes
from sphinx.errors import SphinxError

import aplus_nodes
import translations
import yaml_writer
from directives.abstract_exercise import AbstractExercise
from yaml_writer import ensure_unicode


class ActiveElementInput(AbstractExercise):
    has_content = False
    option_spec = {
        'id': directives.unchanged,
        'class' : directives.class_option,
        'title': directives.unchanged,
        'width': directives.unchanged,
        'url': directives.unchanged,
    }

    def run(self):
        key, difficulty, points = self.extract_exercise_arguments()

        env = self.state.document.settings.env
        name = u"{}_{}".format(env.docname.replace(u'/', u'_'), key)
        override = env.config.override

        classes = []
        if 'class' in self.options:
            classes.extend(self.options['class'])

        # Add document nodes.
        args = {
            u'class': u' '.join(classes),
            u'data-aplus-active-element': u'in',
            u'id': u''+ self.options['id'],
        }
        
        if 'title' in self.options:
          args['data-title'] = self.options['title']
          
        if 'width' in self.options:
          args['style'] = 'width:'+ self.options['width'] + ';'
        
        node = aplus_nodes.html(u'div', args)
        paragraph = aplus_nodes.html(u'p', {})
        paragraph.append(nodes.Text(translations.get(env, 'submit_placeholder')))
        node.append(paragraph)

        key_title = u"{} {}".format(translations.get(env, 'exercise'), key)

        return [node]
