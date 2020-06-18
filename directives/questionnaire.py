# -*- coding: utf-8 -*-
'''
Directives that define automatically assessed questionnaires.
'''
import html
import string

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.errors import SphinxError
from sphinx.util import logging
from sphinx.util.nodes import nested_parse_with_titles

import aplus_nodes
import lib.translations as translations
import lib.yaml_writer as yaml_writer
from directives.abstract_exercise import (AbstractExercise, choice_truefalse,
                                            str_to_bool, choice_enumerate)


logger = logging.getLogger(__name__)


class Questionnaire(AbstractExercise):
    ''' Wraps questionnaire configuration. '''
    has_content = True
    option_spec = {
        'chapter-feedback': directives.flag,
        'weekly-feedback': directives.flag,
        'appendix-feedback': directives.flag,
        'course-feedback': directives.flag,
        'feedback': directives.flag,
        'no-override': directives.flag,
        'pick_randomly': directives.positive_int,
        # Random questions may be resampled after each submission attempt or
        # the questions may be preserved.
        'preserve-questions-between-attempts': directives.flag,
        'submissions': directives.nonnegative_int,
        'points-to-pass': directives.nonnegative_int,
        'title': directives.unchanged,
        'category': directives.unchanged,
        'status': directives.unchanged,
        'show-model': choice_truefalse,
        'reveal-model-at-max-submissions': choice_truefalse,
        'allow-assistant-viewing': choice_truefalse,
        'allow-assistant-grading': choice_truefalse,
    }

    def run(self):
        self.assert_has_content()
        key, difficulty, points = self.extract_exercise_arguments()

        # Parse options.
        classes = [u'exercise']
        is_feedback = False
        if 'chapter-feedback' in self.options:
            classes.append(u'chapter-feedback')
            is_feedback = True
        if 'weekly-feedback' in self.options:
            classes.append(u'weekly-feedback')
            is_feedback = True
        if 'appendix-feedback' in self.options:
            classes.append(u'appendix-feedback')
            is_feedback = True
        if 'course-feedback' in self.options:
            classes.append(u'course-feedback-questionnaire')
            is_feedback = True
        if 'feedback' in self.options:
            is_feedback = True
        if is_feedback:
            key = u'feedback'
            category = u'feedback'
            classes.append(u'feedback')
        else:
            category = u'questionnaire'
            if difficulty:
                classes.append(u'difficulty-' + difficulty)

        if 'category' in self.options:
            category = str(self.options.get('category'))

        env = self.state.document.settings.env
        name = u"{}_{}".format(env.docname.replace(u'/', u'_'), key)
        override = env.config.override

        env.questionnaire_is_feedback = is_feedback
        env.question_count = 0
        env.aplus_single_question_points = None
        env.aplus_quiz_total_points = 0
        env.aplus_pick_randomly_quiz = 'pick_randomly' in self.options
        env.aplus_random_question_exists = False

        # Create document elements.
        node = aplus_nodes.html(u'div', {
            u'class': u' '.join(classes),
            u'data-aplus-exercise': u'yes',
        })
        form = aplus_nodes.html(u'form', {
            u'action': key,
            u'method': u'post',
        })
        nested_parse_with_titles(self.state, self.content, form)

        submit = aplus_nodes.html(u'input', {
            u'type': u'submit',
            u'value': translations.get(env, u'submit'),
            u'class': u'btn btn-primary',
        }, skip_html=True)
        form.append(submit)
        node.append(form)

        # Write configuration file.
        data = {
            u'key': name,
            u'category': category,
            u'difficulty': difficulty or '',
            u'max_submissions': self.options.get('submissions', 0 if is_feedback else env.config.questionnaire_default_submissions),
            u'min_group_size': 1 if is_feedback else env.config.default_min_group_size,
            u'max_group_size': 1 if is_feedback else env.config.default_max_group_size,
            u'points_to_pass': self.options.get('points-to-pass', 0),
            u'feedback': is_feedback,
            u'view_type': u'access.types.stdsync.createForm',
            u'status': self.options.get('status', 'unlisted'),
            u'fieldgroups': [{
                u'title': '',
                u'fields': (u'#!children', None),
            }],
            # The RST source file path is needed for fixing relative URLs
            # in the exercise description.
            '_rst_srcpath': env.doc2path(env.docname, None),
        }

        meta_data = env.metadata[env.app.config.master_doc]
        # Show the model answer after the last submission.
        if 'reveal-model-at-max-submissions' in self.options:
            data['reveal_model_at_max_submissions'] = str_to_bool(self.options['reveal-model-at-max-submissions'])
        else:
            default_reveal = str_to_bool(meta_data.get(
                'questionnaire-default-reveal-model-at-max-submissions', 'false'),
                error_msg_prefix=env.app.config.master_doc + " questionnaire-default-reveal-model-at-max-submissions: ")
            if default_reveal:
                data['reveal_model_at_max_submissions'] = default_reveal
        # Show the model answer after the module deadline.
        if 'show-model' in self.options:
            data['show_model_answer'] = str_to_bool(self.options['show-model'])
        else:
            show_default = str_to_bool(meta_data.get(
                'questionnaire-default-show-model', 'true'),
                error_msg_prefix=env.app.config.master_doc + " questionnaire-default-show-model: ")
            if not show_default:
                data['show_model_answer'] = show_default

        if env.aplus_pick_randomly_quiz:
            pick_randomly = self.options.get('pick_randomly', 0)
            if pick_randomly < 1:
                source, line = self.state_machine.get_source_and_line(self.lineno)
                raise SphinxError(source + ": line " + str(line) +
                    "\nNumber of fields to sample randomly should be greater than zero "
                    "(option pick_randomly in the questionnaire directive).")
            data['fieldgroups'][0]['pick_randomly'] = pick_randomly
            if 'preserve-questions-between-attempts' in self.options:
                data['fieldgroups'][0]['resample_after_attempt'] = False
        elif not env.aplus_random_question_exists:
            # The HTML attribute data-aplus-quiz makes the A+ frontend show the
            # questionnaire feedback in place of the exercise description once
            # the student has submitted at least once. In randomized questionnaires,
            # the same form may not be submitted again due to one-time use nonce
            # values, hence the attribute must not be used in randomized
            # questionnaires.
            node.attributes['data-aplus-quiz'] = 'yes'

        self.set_assistant_permissions(data)

        points_set_in_arguments = len(self.arguments) == 2 and difficulty != self.arguments[1]

        if env.aplus_pick_randomly_quiz:
            calculated_max_points = (
                self.options.get('pick_randomly') * env.aplus_single_question_points
                if env.aplus_single_question_points is not None
                else 0
            )
        else:
            calculated_max_points = env.aplus_quiz_total_points

        if calculated_max_points == 0 and is_feedback:
            data['max_points'] = points
        else:
            if points_set_in_arguments and calculated_max_points != points:
                source, line = self.state_machine.get_source_and_line(self.lineno)
                raise SphinxError(source + ": line " + str(line) +
                    "\nThe points of the questions in the questionnaire must add up to the total points of the questionnaire!")
            data['max_points'] = calculated_max_points

        if 'title' in self.options:
            data['title'] = self.options.get('title')
        else:
            data[u'title|i18n'] = translations.opt('feedback') if is_feedback else translations.opt('exercise', postfix=u" {}".format(key))

        if not 'no-override' in self.options and category in override:
            data.update(override[category])
            if 'url' in data:
                data['url'] = data['url'].format(key=name)

        form.write_yaml(env, name, data, 'exercise')

        return [node]


def slicer(string_list):
  for i in range(0, len(string_list)):
    yield i,string_list[i:i+1]


class QuestionMixin:
    ''' Common functions for all question directives. '''
    option_spec = {
        'class': directives.class_option,
        'required': directives.flag,
        'key': directives.unchanged,
    }

    def create_question(self, title_text=None, points=True):
        env = self.state.document.settings.env
        env.question_count += 1

        # Create base element and data.
        node = aplus_nodes.html(u'div', {
            u'class': u' '.join(self.get_classes()),
        })
        data = {
            u'type': self.grader_field_type(),
            u'extra_info': self.get_extra_info(),
        }
        key = self.options.get('key', None)
        if key:
            data[u'key'] = yaml_writer.ensure_unicode(key)

        # Add title.
        if title_text is not None:
            data[u'title'] = title_text
        elif env.questionnaire_is_feedback:
            data[u'title'] = title_text = u''
        else:
            # "#" in the question title is converted to a number in the MOOC-grader.
            # The questions of a "pick randomly" questionnaire should be numbered
            # in the MOOC-grader since they are randomly selected.
            postfix = '{#}' if env.aplus_pick_randomly_quiz else "{:d}".format(env.question_count)
            data['title|i18n'] = translations.opt('question', postfix=postfix)
            title_text = u"{} {:d}".format(translations.get(env, 'question'), env.question_count)
        if title_text:
            title = aplus_nodes.html(u'label', {})
            title.append(nodes.Text(title_text))
            node.append(title)

        # Add configuration.
        if points and len(self.arguments) > 0:
            question_points = int(self.arguments[0])
            data['points'] = question_points
            env.aplus_quiz_total_points += question_points
            if env.aplus_pick_randomly_quiz:
                if env.aplus_single_question_points is None:
                    env.aplus_single_question_points = question_points
                else:
                    if env.aplus_single_question_points != question_points:
                        source, line = self.state_machine.get_source_and_line(self.lineno)
                        logger.warning("Each question must have equal points when "
                            "the questionnaire uses the 'pick randomly' option.", location=(source, line))

        if 'required' in self.options:
            data[u'required'] = True
        node.set_yaml(data, u'question')

        return env, node, data

    def add_instructions(self, node, data, plain_content):
        if not plain_content:
            return

        parent = aplus_nodes.html(u'div', {})
        parent.store_html(u'more')
        nested_parse_with_titles(self.state, plain_content, parent)
        node.append(parent)

        data[u'more'] = (u'#!html', u'more')

    def add_feedback(self, node, data, paragraph, enumeration_of_choices=None):
        if not paragraph:
            return

        # Add feedback node for rendering without writing to file.
        data[u'feedback'] = (u'#!children', u'feedback')
        feedbacks = aplus_nodes.html(u'p', {u'class':u'feedback-holder'}, no_write=True)

        for i, line in slicer(paragraph):
            if u'§' not in line[0]:
                raise SphinxError(u'Feedback separator § exptected: {}'.format(line[0]))
            value, content = line[0].split(u'§', 1)
            value = value.strip()
            isnot = False
            compare_regexp = False
            if value.startswith('!'):
                isnot = True
                value = value[1:]
            if value.startswith('regexp:'):
                compare_regexp = True
                value = value[7:]

            line[0] = content.strip()

            if enumeration_of_choices:
                if value.startswith('%100%'):
                    line[0] = enumeration_of_choices[value[5:]] + line[0]
                else:
                    line[0] = enumeration_of_choices[value] + line[0]

            # Create document elements.
            hint = aplus_nodes.html(u'div')
            text = aplus_nodes.html(u'p', {})
            text.store_html('hint')
            nested_parse_with_titles(self.state, line, text)
            hint.append(text)
            feedbacks.append(hint)

            # Add configuration data.
            fbdata = {
                u'value': value,
                u'label': (u'#!html', u'hint'),
            }
            if isnot:
                fbdata[u'not'] = True
            if compare_regexp:
                fbdata['compare_regexp'] = True
            hint.set_yaml(fbdata, u'feedback')

        node.append(feedbacks)

    def get_classes(self):
        classes = [u'form-group']
        if 'class' in self.options:
            classes.extend(self.options['class'])
        return classes

    def get_extra_info(self):
        return {
            u'class': u' '.join(self.get_classes()),
        }

    def grader_field_type(self):
        return u'undefined'


class Choice(QuestionMixin, Directive):
    ''' Abstract directive that includes answer options. '''
    option_spec = dict(QuestionMixin.option_spec)
    option_spec['enumerate'] = choice_enumerate
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False

    def run(self):
        self.assert_has_content()

        # Detect paragraphs: any number of plain content, choices and optional feedback.
        empty_lines = list(loc for loc,line in enumerate(self.content) if line == u'')
        plain_content = None
        choices = []
        feedback = []
        if len(empty_lines) > 0:
            last = self.content[(empty_lines[-1] + 1):]

            def split_second_last(empty_lines):
                if len(empty_lines) > 1:
                    return self.content[:empty_lines[-2]], self.content[(empty_lines[-2] + 1):empty_lines[-1]]
                else:
                    return None, self.content[:empty_lines[-1]]

            # Backwards compatibility for skipping feedback paragraph.
            if len(last) == 1 and last[0].startswith(u'I hereby declare that no feedback '):
                plain_content, choices = split_second_last(empty_lines)
            elif all(u'§' in line for line in last):
                plain_content, choices = split_second_last(empty_lines)
                feedback = last
            else:
                plain_content = self.content[:empty_lines[-1]]
                choices = last
        else:
            choices = self.content

        # Create question.
        env, node, data = self.create_question()
        self.add_instructions(node, data, plain_content)
        data[u'options'] = (u'#!children', u'option')
        if 'partial-points' in self.options:
            data['partial_points'] = True

        dropdown = None
        if self.grader_field_type() == 'dropdown':
            # The HTML select element has a different structure compared
            # to the input elements (radio buttons and checkboxes).
            dropdown = aplus_nodes.html('select', {
                'name': 'field_{:d}'.format(env.question_count - 1),
            })

        correct_count = 0
        # Travel all answer options.
        enumeration_of_choices = {}
        for i, line in slicer(choices):

            # Split choice key off.
            key, content = line[0].split(u' ', 1)
            key = key.strip()
            line[0] = content.strip()

            # Trim the key.
            correct = False
            selected = False
            if key.startswith('+'):
                selected = True
                key = key[1:]
            if key.startswith('*'):
                correct = True
                key = key[1:]
                correct_count += 1
            elif key.startswith('?'):
                correct = "neutral"
                key = key[1:]
            if key.endswith('.'):
                key = key[:-1]

            # Add YAML configuration data.
            optdata = {
                'value': key,
            }
            if correct:
                optdata['correct'] = correct
            if selected:
                optdata['selected'] = True

            if "enumerate" in self.options:
                if self.options['enumerate'] == 'numeric':
                    prefix = str(i+1) + ". "
                else:
                    # Start over if there are more than 26 options.
                    prefix = list(string.ascii_lowercase)[i % 26] + ": "
                line[0] = prefix + line[0]
                enumeration_of_choices[key] = prefix

            # Create document elements.
            if dropdown is None:
                # One answer alternative as a radio button or a checkbox.
                choice = aplus_nodes.html('div', {'class': 'radio'})
                label = aplus_nodes.html('label', {})
                attrs = {
                    'type': self.input_type(),
                    'name': 'field_{:d}'.format(env.question_count - 1),
                    'value': key,
                }
                if selected:
                    attrs['checked'] = 'checked'
                label.append(aplus_nodes.html('input', attrs))
                choice.append(label)
                node.append(choice)

                text = aplus_nodes.html('span', {})
                text.store_html('label')
                nested_parse_with_titles(self.state, line, text)
                label.append(text)

                optdata['label'] = ('#!html', 'label')
                choice.set_yaml(optdata, 'option')
            else:
                # Add option elements to the select.
                # Options may only contain plain text, not formatted HTML.
                attrs = {
                    'value': key,
                }
                if selected:
                    attrs['selected'] = 'selected'
                option = aplus_nodes.html('option', attrs)
                text = line[0]
                option.append(nodes.Text(text))
                dropdown.append(option)
                optdata['label'] = html.escape(text)
                option.set_yaml(optdata, 'option')

        if dropdown is not None:
            node.append(dropdown)

        if 'randomized' in self.options:
            data['randomized'] = self.options.get('randomized', 1)
            if data['randomized'] > len(choices):
                source, line = self.state_machine.get_source_and_line(self.lineno)
                raise SphinxError(source + ": line " + str(line) +
                    "\nThe option 'randomized' can not be greater than the number of answer choices!")
            if 'correct-count' in self.options:
                data['correct_count'] = self.options.get('correct-count', 0)
                if data['correct_count'] > correct_count or data['correct_count'] > data['randomized']:
                    source, line = self.state_machine.get_source_and_line(self.lineno)
                    raise SphinxError(source + ": line " + str(line) +
                        "\nThe option 'correct-count' can not be greater than "
                        "the number of correct choices or the value of 'randomized'!")
            if 'preserve-questions-between-attempts' in self.options:
                data['resample_after_attempt'] = False
            env.aplus_random_question_exists = True

        self.add_feedback(node, data, feedback, enumeration_of_choices)

        return [node]


class SingleChoice(Choice):
    ''' Lists options for picking the correct one. '''

    # Inherit option_spec from Choice and add a key.
    option_spec = dict(Choice.option_spec)
    option_spec['dropdown'] = directives.flag

    def form_group_class(self):
        return u'form-pick-one'

    def grader_field_type(self):
        if 'dropdown' in self.options:
            return 'dropdown'
        return u'radio'

    def input_type(self):
        return u'radio'


class MultipleChoice(Choice):
    ''' Lists options for picking all the correct ones. '''

    # Inherit Choice options and add a key.
    option_spec = dict(Choice.option_spec)
    option_spec.update({
        # enable partial points for partially correct answers
        'partial-points': directives.flag,
        # randomized and correct-count are used together:
        # randomized defines the number of options that are chosen randomly and
        # correct-count is the number of correct options to include
        'randomized': directives.positive_int,
        'correct-count': directives.nonnegative_int,
        # Random questions may be resampled after each submission attempt or
        # the questions may be preserved.
        'preserve-questions-between-attempts': directives.flag,
    })

    def form_group_class(self):
        return u'form-pick-any'

    def grader_field_type(self):
        return u'checkbox'

    def input_type(self):
        return u'checkbox'


class FreeText(QuestionMixin, Directive):
    ''' A free text answer. '''
    has_content = True
    required_arguments = 0
    optional_arguments = 2
    final_argument_whitespace = False
    option_spec = {
        'length': directives.positive_int,
        'height': directives.positive_int,
        'own-line': directives.flag,
        'main-feedback': directives.flag,
        'required': directives.flag,
        'no-standard-prompt': directives.flag,
        'shorter-prompt': directives.flag,
        'class': directives.class_option,
        'key': directives.unchanged,
        'extra': directives.unchanged,
    }

    def run(self):
        self.length = self.options.get('length', None)
        self.height = self.options.get('height', 1)
        self.position = u'place-on-own-line' if self.height > 1 or u'own-line' in self.options else u'place-inline'

        # Detect paragraphs: any number of plain content and correct answer including optional feedback
        plain_content = None
        config_content = []
        env = self.state.document.settings.env
        if env.questionnaire_is_feedback:
            plain_content = self.content
        else:
            empty_lines = list(loc for loc,line in enumerate(self.content) if line == u"")
            if len(empty_lines) > 0:
                plain_content = self.content[:empty_lines[-1]]
                config_content = self.content[(empty_lines[-1] + 1):]
            else:
                config_content = self.content

        # Create question.
        env, node, data = self.create_question()
        self.add_instructions(node, data, plain_content)

        # Create input element.
        if self.height > 1:
            attrs = {
                u'rows': self.height,
                u'class': self.position,
            }
            if self.length:
                attrs[u'cols'] = self.length
            element = aplus_nodes.html(u'textarea', attrs)
        else:
            attrs = {
                u'type': u'text',
                u'class': self.position,
            }
            if self.length:
                attrs[u'size'] = self.length
            element = aplus_nodes.html(u'input', attrs)
        node.append(element)

        # Add configuration.
        if len(self.arguments) > 1:
            self._validate_compare_method(self.arguments[1])
            data[u'compare_method'] = self.arguments[1]

        if config_content:
            fb = None
            if u'§' in config_content[0]:
                correct,fb = config_content[0].split(u'§', 1)
            else:
                correct = config_content[0]
                config_content = config_content[1:]
            if u'°=°' in correct:
                correct,model = correct.split(u'°=°', 1)
                data[u'model'] = model.strip().replace(u"°°°", u"\n")
                if fb:
                    config_content[0] = correct.strip() + u" § " + fb.strip()
            data[u'correct'] = correct.strip().replace(u"°°°", u"\n")
            self.add_feedback(node, data, config_content)

        return [node]

    def get_classes(self):
        classes = super(FreeText, self).get_classes()
        if 'main-feedback' in self.options:
            classes.append(u'main-feedback-question')
        if 'required' in self.options:
            classes.append(u'required')
        else:
            classes.append(u'voluntary')
        if not 'no-standard-prompt' in self.options:
            classes.append(u'standard')
        if 'shorter-prompt' in self.options:
            classes.append(u'shorter')
        classes.append(self.position)
        return classes

    def get_extra_info(self):
        data = super(FreeText, self).get_extra_info()
        for entry in self.options.get('extra', '').split(u';'):
            parts = entry.split(u'=', 1)
            if len(parts) == 2:
                try:
                    parts[1] = int(parts[1])
                except ValueError:
                    pass
                data[parts[0]] = parts[1]
        return data

    def grader_field_type(self):
        return u'textarea' if self.height > 1 else u'text'

    def _validate_compare_method(self, method):
        # valid_t and valid_mods should reflect those specified in mooc-grader
        # See also mooc-grader/README.md and mooc-grader/access/forms.py method compare_values
        valid_t = {'array', 'unsortedchars', 'string', 'regexp', 'int', 'float', 'subdiff'}
        # 'requirecase' has an effect only when used with 'string'.
        # TODO: raise an exception when using 'requirecase' with something else
        valid_mods = {'ignorerepl', 'ignorews', 'ignorequotes', 'ignoreparenthesis', 'requirecase'}

        parts = method.split('-')
        t = parts[0]
        mods = parts[1:]

        if t not in valid_t:
            raise SphinxError('Unknown compare method: %s' % t)
        for mod in mods:
            if mod not in valid_mods:
                raise SphinxError('Unknown compare method modifier: %s' % mod)


class AgreeGroup(Directive):
    ''' Groups agree items together. '''
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'class' : directives.class_option,
    }

    def run(self):
        # This directive is obsolete, AgreeItems can be placed alone.
        classes = [u'form-group']
        if 'class' in self.options:
            classes.extend(self.options['class'])
        node = aplus_nodes.html(u'div', { u'class': u" ".join(classes) })
        nested_parse_with_titles(self.state, self.content, node)
        return  [node]


class AgreeItem(QuestionMixin, Directive):
    ''' Question presenting an agreement scale. '''
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        env, node, data = self.create_question(title_text=self.arguments[0], points=False)
        data[u'options'] = self.generate_options(env, node)
        return [node]

    def generate_options(self, env, node):
        options = []
        for i, key in enumerate(['agreement4', 'agreement3', 'agreement2', 'agreement1', 'agreement0']):
            options.append({
                u'value': 4 - i,
                u'label|i18n': translations.opt(key),
            })
            choice = aplus_nodes.html(u'div', {u'class':u'radio'})
            label = aplus_nodes.html(u'label', {})
            label.append(aplus_nodes.html(u'input', {
                u'type': u'radio',
                u'name': u'field_{:d}'.format(env.question_count - 1),
                u'value': 4 - i,
            }))
            label.append(nodes.Text(translations.get(env, key)))
            choice.append(label)
            node.append(choice)
        return options


    def grader_field_type(self):
        return u'radio'


class AgreeItemGenerate(AgreeItem):
    ''' Generates questions presenting an agreement scale. '''
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'config' : directives.unchanged,
        'class' : directives.class_option,
        'required': directives.flag,
        'key': directives.unchanged,
    }

    def run(self):
        env = self.state.document.settings.env

        if not 'config' in self.options:
            raise SphinxError('Config option is required')
        import os
        path = os.path.join(env.app.srcdir, self.options['config'])
        if not os.path.exists(path):
            raise SphinxError('Missing config path {}'.format(self.options['config']))
        item_list = yaml_writer.read(path)

        itemnodes = []
        for item in item_list:
            title, info, img = [item.get(u"title", u""), item.get(u"info", u""), item.get(u"image_url", u"")]
            _, node, data = self.create_question(title_text=self.arguments[0].replace(u"$title", title), points=False)

            more = u""
            if img:
                e = aplus_nodes.html(u"p", {u"class": u"indent"})
                e.append(aplus_nodes.html(u"img", {u"src":img, u"alt": title, u"style": u"max-height:100px;"}))
                node.append(e)
                more += str(e)
            if info:
                e = aplus_nodes.html(u"p", {u"class": u"indent"})
                e.append(nodes.Text(info))
                node.append(e)
                more += str(e)

            data[u'options'] = self.generate_options(env, node)
            data[u'more'] = more
            itemnodes.append(node)

        return itemnodes
