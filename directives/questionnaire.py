# -*- coding: utf-8 -*-
'''
Directives that define automatically assessed questionnaires.
'''
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.errors import SphinxError
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles

import aplus_nodes
import translations
from directives.abstract_exercise import AbstractExercise


class Questionnaire(AbstractExercise):
    ''' Wraps questionnaire configuration. '''
    has_content = True
    option_spec = {
        'chapter-feedback': directives.flag,
        'weekly-feedback': directives.flag,
        'appendix-feedback': directives.flag,
        'course-feedback': directives.flag,
        'feedback': directives.flag,
        'submissions': directives.nonnegative_int,
        'points-to-pass': directives.nonnegative_int,
    }

    def run(self):
        self.assert_has_content()
        key, category, points = self.extract_exercise_arguments()

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
            category = category or u'feedback'
            classes.append(u'feedback')
        else:
            category = category or u'exercise'

        env = self.state.document.settings.env
        name = u"{}_{}".format(env.docname.replace(u'/', u'_'), key)

        env.questionnaire_is_feedback = is_feedback
        env.question_count = 0

        # Create document elements.
        node = aplus_nodes.html(u'div', {
            u'class': u' '.join(classes),
            u'data-aplus-exercise': u'yes',
            u'data-aplus-quiz': u'yes',
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
        })
        form.append(submit)
        node.append(form)

        # Write configuration file.
        data = {
            'key': name,
            'category': category,
            'max_points': points,
            'max_submissions': self.options.get('submissions', 0 if is_feedback else env.config.questionnaire_default_submissions),
            'min_group_size': 1 if is_feedback else env.config.default_min_group_size,
            'max_group_size': 1 if is_feedback else env.config.default_max_group_size,
            'points_to_pass': self.options.get('points-to-pass', 0),
            'feedback': is_feedback,
            'view_type': 'access.types.stdsync.createForm',
            'title|i18n': translations.opt('feedback') if is_feedback else translations.opt('exercise', postfix=u" {}".format(key)),
            'fieldgroups': [{
                'title': '',
                'fields': ('#!children', None),
            }],
        }
        form.write_yaml(env, name, data, 'exercise')

        return [node]


def slicer(string_list):
  for i in range(0, len(string_list)):
    yield i,string_list[i:i+1]


class QuestionMixin:
    ''' Common functions for all question directives. '''
    option_spec = {
        'class' : directives.class_option,
        'required': directives.flag,
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
        }

        # Add title.
        if not title_text is None:
            data['title'] = title_text
        elif env.questionnaire_is_feedback:
            data['title'] = title_text = u''
        else:
            data['title|i18n'] = translations.opt('question', postfix=u" {:d}".format(env.question_count))
            title_text = u"{} {:d}".format(translations.get(env, 'question'), env.question_count)
        if title_text:
            title = aplus_nodes.html(u'label', {})
            title.append(nodes.Text(title_text))
            node.append(title)

        # Add configuration.
        if points and len(self.arguments) > 0:
            data['points'] = int(self.arguments[0])
        if 'required' in self.options:
            data['required'] = True
        node.set_yaml(data, 'question')

        return env, node, data

    def add_instructions(self, node, data, plain_content):
        if not plain_content:
            return

        parent = aplus_nodes.html(u'div', {})
        parent.store_html('more')
        nested_parse_with_titles(self.state, plain_content, parent)
        node.append(parent)

        data['more'] = ('#!html', 'more')

    def add_feedback(self, node, data, paragraph):
        if not paragraph:
            return

        # Add feedback node for rendering without writing to file.
        data['feedback'] = ('#!children', 'feedback')
        feedbacks = aplus_nodes.html(u'p', {u'class':u'feedback-holder'}, no_write=True)

        for i,line in slicer(paragraph):
            if not u'§' in line[0]:
                raise SphinxError(u'Feedback separator § exptected: {}'.format(line[0]))
            value,content = line[0].split(u'§', 1)
            value = value.strip()
            line[0] = content.strip()
            isnot = False
            if value.startswith(u'!'):
                isnot = True
                value = value[1:]

            # Create document elements.
            hint = aplus_nodes.html(u'div')
            text = aplus_nodes.html(u'p', {})
            text.store_html('hint')
            nested_parse_with_titles(self.state, line, text)
            hint.append(text)
            feedbacks.append(hint)

            # Add configuration data.
            fbdata = {
                'value': value,
                'label': ('#!html', 'hint'),
            }
            if isnot:
                fbdata['not'] = True
            hint.set_yaml(fbdata, 'feedback')

        node.append(feedbacks)

    def get_classes(self):
        classes = [u'form-group']
        if 'class' in self.options:
            classes.extend(self.options['class'])
        return classes

    def grader_field_type(self):
        return u'undefined'


class Choice(QuestionMixin, Directive):
    ''' Abstract directive that includes answer options. '''
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
        data['options'] = ('#!children', 'option')

        # Travel all answer options.
        for i,line in slicer(choices):

            # Split choice key off.
            key,content = line[0].split(u' ', 1)
            key = key.strip()
            line[0] = content.strip()

            # Trim the key.
            correct = False
            if key.startswith(u'*'):
                correct = True
                key = key[1:]
            if key.endswith(u'.'):
                key = key[:-1]

            # Create document elements.
            choice = aplus_nodes.html(u'div', {u'class':u'radio'})
            label = aplus_nodes.html(u'label', {})
            label.append(aplus_nodes.html(u'input', {
                u'type': self.input_type(),
                u'name': u'field_{:d}'.format(env.question_count - 1),
                u'value': key,
            }))
            choice.append(label)
            node.append(choice)

            text = aplus_nodes.html(u'span', {})
            text.store_html(u'label')
            nested_parse_with_titles(self.state, line, text)
            label.append(text)

            # Add configuration data.
            optdata = {
                'value': key,
                'label': ('#!html', 'label'),
            }
            if correct:
                optdata['correct'] = True
            choice.set_yaml(optdata, 'option')

        self.add_feedback(node, data, feedback)

        return [node]


class SingleChoice(Choice):
    ''' Lists options for picking the correct one. '''

    def form_group_class(self):
        return u'form-pick-one'

    def grader_field_type(self):
        return 'radio'

    def input_type(self):
        return u'radio'


class MultipleChoice(Choice):
    ''' Lists options for picking all the correct ones. '''

    def form_group_class(self):
        return u'form-pick-any'

    def grader_field_type(self):
        return 'checkbox'

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
    }

    def run(self):
        self.length = self.options.get('length', 50)
        self.height = self.options.get('height', 1)
        position = u'place-on-own-line' if self.height > 1 or u'own-line' in self.options else u'place-inline'

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
            element = aplus_nodes.html(u'textarea', {
                u'rows': self.height,
                u'cols': self.length,
                u'class': position,
            })
        else:
            element = aplus_nodes.html(u'input', {
                u'type': u'text',
                u'size': self.length,
                u'class': position,
            })
        node.append(element)

        # Add configuration.
        if len(self.arguments) > 1:
            data['compare_method'] = self.arguments[1]
        if config_content:
            if u'§' in config_content[0]:
                data['correct'] = config_content[0].split(u'§', 1)[0].strip()
            else:
                data['correct'] = config_content[0].strip()
                config_content = config_content[1:]
            self.add_feedback(node, data, config_content)

        return [node]

    def grader_field_type(self):
        return u'textarea' if self.height > 1 else u'text'

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
        return classes


class AgreeGroup(Directive):
    ''' Groups agree items together. '''
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        # This directive is obsolete, AgreeItems can be placed alone.
        node = aplus_nodes.html(u'div', {u'class':u'agreement-group'})
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
        options = []

        for i, key in enumerate(['agreement4', 'agreement3', 'agreement2', 'agreement1', 'agreement0']):
            options.append({
                'value': 4 - i,
                'label|i18n': translations.opt(key),
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

        data['options'] = options
        return [node]

    def grader_field_type(self):
        return 'radio'
