# -*- coding: utf-8 -*-
'''
Directive that places active element output divs.
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



class ActiveElementOutput(AbstractExercise):
    has_content = False
    option_spec = {
        'class' : directives.class_option,
        'submissions': directives.nonnegative_int,
        'config': directives.unchanged,
        'url': directives.unchanged,
        'title': directives.unchanged,
        'inputs': directives.unchanged,
        'width': directives.unchanged,
        'height': directives.unchanged,
        'clear': directives.unchanged,
        'type': directives.unchanged,
        'scale-size': directives.flag,
        'status': directives.unchanged,
    }

    def run(self):
        key, difficulty, points = self.extract_exercise_arguments()

        env = self.state.document.settings.env
        name = u"{}_{}".format(env.docname.replace(u'/', u'_'), key)
        override = env.config.override

        classes = [u'exercise']
        if 'class' in self.options:
            classes.extend(self.options['class'])

        # Add document nodes.
        args = {
            u'class': u' '.join(classes),
            u'data-aplus-exercise': u'yes',
            u'data-aplus-active-element': u'out',
            u'data-inputs': u''+ self.options.get('inputs', ''),
        }

        if 'inputs' not in self.options:
            raise self.warning("The input list for output '{:s}' is empty.".format(key))

        if 'type' in self.options:
            args['data-type'] = self.options['type']
        else:
            args['data-type'] = 'text'

        if 'scale-size' in self.options:
            args['data-scale'] = ''

        if 'title' in self.options:
            args['data-title'] = self.options['title']

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
            config_title = None

        config_title = self.options.get('title', config_title)

        category = u'submit'
        data.update({
            u'key': name,
            u'title': env.config.submit_title.format(
                key_title=key_title, config_title=config_title
            ),
            u'category': u'active elements',
            u'max_submissions': self.options.get('submissions', data.get('max_submissions', env.config.ae_default_submissions)),
        })
        data.setdefault('status', self.options.get('status', 'unlisted'))
        if category in override:
            data.update(override[category])
            if 'url' in data:
                data['url'] = data['url'].format(key=name)

        node.write_yaml(env, name, data, 'exercise')

        return [node]
