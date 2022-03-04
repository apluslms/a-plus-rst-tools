# -*- coding: utf-8 -*-
'''
Directive that places exercise submission forms.
'''
import os.path
from docutils.parsers.rst import directives
from docutils import nodes
from sphinx.errors import SphinxError
from sphinx.util.nodes import nested_parse_with_titles

import aplus_nodes
import lib.translations as translations
import lib.yaml_writer as yaml_writer
from directives.abstract_exercise import ConfigurableExercise, choice_truefalse
from lib.revealrule import parse_reveal_rule


class SubmitForm(ConfigurableExercise):
    has_content = True
    option_spec = ConfigurableExercise.option_spec.copy()
    option_spec.update({
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
        'lti_aplus_get_and_post': directives.flag,
        'lti_open_in_iframe': directives.flag,
        'radar_tokenizer': directives.unchanged,
        'radar_minimum_match_tokens': directives.unchanged,
        'status': directives.unchanged,
        'allow-assistant-viewing': choice_truefalse,
        'allow-assistant-grading': choice_truefalse,
        'reveal-submission-feedback': directives.unchanged,
        'reveal-model-solutions': directives.unchanged,
        'grading-mode': directives.unchanged,
    })

    def run(self):
        key, difficulty, points = self.extract_exercise_arguments()

        env = self.state.document.settings.env
        name = "{}_{}".format(env.docname.replace('/', '_'), key)

        classes = ['exercise']
        if 'class' in self.options:
            classes.extend(self.options['class'])
        if difficulty:
            classes.append('difficulty-' + difficulty)

        # Add document nodes.
        args = {
            'class': ' '.join(classes),
            'data-aplus-exercise': 'yes',
        }
        if 'quiz' in self.options:
            args['data-aplus-quiz'] = 'yes'
        if 'ajax' in self.options:
            args['data-aplus-ajax'] = 'yes'
        node = aplus_nodes.html('div', args)

        key_title = "{} {}".format(translations.get(env, 'exercise'), key)

        # Load or create exercise configuration.
        if 'config' in self.options:
            path = os.path.join(env.app.srcdir, self.options['config'])
            if not os.path.exists(path):
                raise SphinxError('Missing config path {}'.format(self.options['config']))
            data = yaml_writer.read(path)
            config_title = data.get('title', '')
        else:
            data = { '_external': True }
            if 'url' in self.options:
                data['url'] = self.options['url']
            if 'lti' in self.options:
                data.update({
                    'lti': self.options['lti'],
                    'lti_context_id': self.options.get('lti_context_id', ''),
                    'lti_resource_link_id': self.options.get('lti_resource_link_id', ''),
                })
                if 'lti_aplus_get_and_post' in self.options:
                    data.update({'lti_aplus_get_and_post': True})
                if 'lti_open_in_iframe' in self.options:
                    data.update({'lti_open_in_iframe': True})
            config_title = ''

        config_title = self.options.get('title', config_title)
        if "radar_tokenizer" in self.options or "radar_minimum_match_tokens" in self.options:
            data['radar_info'] = {
                'tokenizer': self.options.get("radar_tokenizer"),
                'minimum_match_tokens': self.options.get("radar_minimum_match_tokens"),
            }

        category = 'submit'
        data.update({
            'key': name,
            'category': 'submit',
            'scale_points': points,
            'difficulty': difficulty or '',
            'max_submissions': self.options.get('submissions', data.get('max_submissions', env.config.program_default_submissions)),
            'min_group_size': data.get('min_group_size', env.config.default_min_group_size),
            'max_group_size': data.get('max_group_size', env.config.default_max_group_size),
            'points_to_pass': self.options.get('points-to-pass', data.get('points_to_pass', 0)),
            # The RST source file path is needed for fixing relative URLs
            # in the exercise description.
            # Replace the Windows path separator backslash \ with the Unix forward slash /.
            '_rst_srcpath': env.doc2path(env.docname, None).replace('\\', '/'),
        })
        self.set_assistant_permissions(data)

        if data.get('title|i18n'):
            # Exercise config.yaml defines title|i18n for multiple languages.
            # Do not write the field "title" to data in order to avoid conflicts.
            if config_title:
                # Overwrite the title for one language since the RST directive
                # has defined the title option (or alternatively, the yaml file
                # has "title" in addition to "title|i18n", but that does not make sense).
                # env.config.language may be incorrect if the language can not be detected.
                data['title|i18n'][env.config.language] = env.config.submit_title.format(
                    key_title=key_title, config_title=config_title
                )
        else:
            formatted_title = env.config.submit_title.format(
                key_title=key_title, config_title=config_title
            )
            # If no title has been defined, use key_title as the default.
            data['title'] = formatted_title if formatted_title else key_title

        if self.content:
            self.assert_has_content()
            # Sphinx can not compile the nested RST into HTML at this stage, hence
            # the HTML instructions defined in this directive body are added to
            # the exercise YAML file only at the end of the build. Sphinx calls
            # the visit functions of the nodes in the last writing phase.
            # The instructions are added to the YAML file in the depart_html
            # function in aplus_nodes.py.
            exercise_description = aplus_nodes.html('div', {})
            exercise_description.store_html('exercise_description')
            nested_parse_with_titles(self.state, self.content, exercise_description)
            node.append(exercise_description)
            data['instructions'] = ('#!html', 'exercise_description')
        else:
            # The placeholder text is only used in the built HTML
            # (not in the YAML configurations).
            paragraph = aplus_nodes.html('p', {})
            paragraph.append(nodes.Text(translations.get(env, 'submit_placeholder')))
            node.append(paragraph)

        data.setdefault('status', self.options.get('status', 'unlisted'))

        source, line = self.state_machine.get_source_and_line(self.lineno)
        if 'reveal-submission-feedback' in self.options:
            data['reveal_submission_feedback'] = parse_reveal_rule(
                self.options['reveal-submission-feedback'],
                source,
                line,
                'reveal-submission-feedback',
            )
        if 'reveal-model-solutions' in self.options:
            data['reveal_model_solutions'] = parse_reveal_rule(
                self.options['reveal-model-solutions'],
                source,
                line,
                'reveal-model-solutions',
            )

        if 'grading-mode' in self.options:
            data['grading_mode'] = self.options['grading-mode']

        self.apply_override(data, category)
        self.set_url(data, name)

        if "lti" in data:
            self.options['no-configure'] = None

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

        if 'category' in self.options:
            data['category'] = str(self.options['category'])

        node.write_yaml(env, name, data, 'exercise')

        return [node]
