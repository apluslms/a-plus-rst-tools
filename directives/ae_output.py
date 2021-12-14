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
from directives.abstract_exercise import ConfigurableExercise


class ActiveElementOutput(ConfigurableExercise):
    has_content = False
    option_spec = ConfigurableExercise.option_spec.copy()
    option_spec.update({
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
    })

    def run(self):
        key, difficulty, points = self.extract_exercise_arguments()

        env = self.state.document.settings.env
        name = "{}_{}".format(env.docname.replace('/', '_'), key)
        override = env.config.override

        classes = ['exercise']
        if 'class' in self.options:
            classes.extend(self.options['class'])

        # Add document nodes.
        args = {
            'class': ' '.join(classes),
            'data-aplus-exercise': 'yes',
            'data-aplus-active-element': 'out',
            'data-inputs': ''+ self.options.get('inputs', ''),
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

        node = aplus_nodes.html('div', args)
        paragraph = aplus_nodes.html('p', {})
        paragraph.append(nodes.Text(translations.get(env, 'submit_placeholder')))
        node.append(paragraph)

        key_title = "{} {}".format(translations.get(env, 'exercise'), key)

        # Load or create exercise configuration.
        if 'config' in self.options:
            path = os.path.join(env.app.srcdir, self.options['config'])
            if not os.path.exists(path):
                raise SphinxError('Missing config path {}'.format(self.options['config']))
            data = yaml_writer.read(path)
            config_title = data.get('title', None)
        else:
            data = { '_external': True }
            if 'url' in self.options:
                data['url'] = self.options['url']
            config_title = None

        config_title = self.options.get('title', config_title)

        category = 'submit'
        data.update({
            'key': name,
            'title': env.config.submit_title.format(
                key_title=key_title, config_title=config_title
            ),
            'category': 'active elements',
            'max_submissions': self.options.get('submissions', data.get('max_submissions', env.config.ae_default_submissions)),
        })
        data.setdefault('status', self.options.get('status', 'unlisted'))

        self.apply_override(data, category)
        self.set_url(data, name)

        configure_files = {}
        if "container" in data and isinstance(data["container"], dict) and "mount" in data["container"]:
            configure_files[data["container"]["mount"]] = data["container"]["mount"]
        if "template" in data:
            configure_files[data["template"]] = data["template"]
        if "feedback_template" in data:
            configure_files[data["feedback_template"]] = data["feedback_template"]
        if "instructions_file" in data:
            configure_files[data["instructions_file"]] = data["instructions_file"]

        self.set_configure(data, data.get("url"), configure_files)

        node.write_yaml(env, name, data, 'exercise')

        return [node]
