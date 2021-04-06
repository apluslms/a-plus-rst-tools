# -*- coding: utf-8 -*-
'''
Directive that places active element inputs.
'''
import os.path
from docutils.parsers.rst import directives
from docutils import io, nodes, utils
from sphinx.errors import SphinxError
from sphinx.util import logging

import aplus_nodes
import lib.translations as translations
import lib.yaml_writer as yaml_writer
from directives.abstract_exercise import AbstractExercise

from docutils.utils.error_reporting import SafeString, ErrorString

logger = logging.getLogger(__name__)


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
        'file': directives.unchanged,
    }

    def run(self):

        if len(self.arguments) > 0:
            key = self.arguments[0]
        else:
            raise SphinxError('Missing active element input id')

        env = self.state.document.settings.env

        name = "{}_{}".format(env.docname.replace('/', '_'), key)
        override = env.config.override

        classes = []
        if 'class' in self.options:
            classes.extend(self.options['class'])

        # Add document nodes.
        args = {
            'class': ' '.join(classes),
            'data-aplus-active-element': 'in',
            'id': ''+ key,
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

        node = aplus_nodes.html('div', args)
        paragraph = aplus_nodes.html('p', {})
        paragraph.append(nodes.Text(translations.get(env, 'active_element_placeholder')))
        node.append(paragraph)

        # For clickable inputs the pre-generated html
        # needs to be added after the regular a+ exercise node
        if 'type' in self.options and self.options['type'] == 'clickable':
            if 'file' not in self.options:
                logger.warning('Clickable active element input "{}" missing template file.'
                                .format(name), location=node)
                return [node]

            # Read given html file (from docutils.directives.misc.raw)
            source_dir = os.path.dirname(
                os.path.abspath(self.state.document.current_source))
            path = os.path.join(env.app.srcdir, self.options['file'])
            path = utils.relative_path(None, path)
            try:
                raw_file = io.FileInput(source_path=path,
                                        encoding=self.state.document.settings.input_encoding,
                                        error_handler=self.state.document.settings.input_encoding_error_handler)
            except IOError as error:
                logger.error('Problem with "%s" directive:\n%s.'
                                  % (self.name, ErrorString(error)), location=node)
                return []
            try:
                text = raw_file.read()
            except UnicodeError as error:
                logger.error('Problem with "%s" directive:\n%s.'
                                  % (self.name, ErrorString(error)), location=node)
                return []

            # Generate raw node
            rawnode = nodes.raw('', text, **{'format':'html'})
            wrapnode = aplus_nodes.html('div', {'id': ''+ key + '-wrap','class': 'clickable-ae-wrapper'})
            wrapnode.append(node)
            wrapnode.append(rawnode)
            return [wrapnode]

        return [node]
