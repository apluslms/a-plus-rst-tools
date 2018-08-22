# -*- coding: utf-8 -*-
'''
Directive that places active element inputs.
'''
import os.path
from docutils.parsers.rst import directives
from docutils import nodes
from sphinx.errors import SphinxError

import aplus_nodes
import lib.translations as translations
import lib.yaml_writer as yaml_writer
from directives.abstract_exercise import AbstractExercise
from lib.yaml_writer import ensure_unicode


class ActiveElementInput(AbstractExercise):
    has_content = False
    option_spec = {
        'class' : directives.class_option,
        'title': directives.unchanged,
        'width': directives.unchanged,
        'height': directives.unchanged,
        'clear': directives.unchanged,
        'default': directives.unchanged,
        'type': directives.unchanged,
    }

    def run(self):

        if len(self.arguments) > 0:
            key = self.arguments[0]
        else:
            raise SphinxError('Missing active element input id')

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
            u'id': u''+ key,
        }

        if 'title' in self.options:
            args['data-title'] = self.options['title']

        if 'default' in self.options:
            args['data-default'] = self.options['default']

        if 'type' in self.options:
            args['data-type'] = self.options['type']

        if 'width' in self.options:
            args['style'] = 'width:'+ self.options['width'] + ';'

        if 'height' in self.options:
            if 'style' not in args:
                args['style'] = 'height:'+ self.options['height'] + ';'
            else:
                args['style'] = args['style'] + 'height:'+ self.options['height'] + ';'

        if 'clear' in self.options:
          args['style'] = args['style'] + 'clear:'+ self.options['clear'] + ';'

        node = aplus_nodes.html(u'div', args)
        paragraph = aplus_nodes.html(u'p', {})
        paragraph.append(nodes.Text(translations.get(env, 'active_element_placeholder')))
        node.append(paragraph)

        return [node]
