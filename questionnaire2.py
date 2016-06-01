'''
Adds support for directives that define automatically assessed questionnaires.
'''
from docutils.parsers.rst import directives
from docutils import nodes
from sphinx.errors import SphinxError
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
import itertools
import aplus_nodes
import toc_config


def extract_points(arg):
    category = 'exercise'
    points = 0
    if not arg is None:
        for is_number, chars in itertools.groupby(arg, key=str.isdigit):
            if is_number:
                points = int(''.join(chars))
            else:
                category = ''.join(chars)
    return category, points


class Questionnaire(Directive):
    ''' Wraps questionnaire configuration. '''
    has_content = True
    required_arguments = 0
    optional_arguments = 2
    final_argument_whitespace = False
    option_spec = {
        'chapter-feedback': directives.flag,
        'weekly-feedback': directives.flag,
        'course-feedback': directives.flag,
        'feedback': directives.flag,
    }

    def run(self):
        self.assert_has_content()

        # Parse arguments and options.
        key = self.arguments[0] if len(self.arguments) > 0 else 'unknown'
        category, points = extract_points(self.arguments[1] if len(self.arguments) > 1 else None)

        is_feedback = False
        classes = ['exercise']
        if 'chapter-feedback' in self.options:
            is_feedback = True
            classes.extend(['feedback', 'chapter-feedback'])
            key = 'feedback'
        if 'weekly-feedback' in self.options:
            is_feedback = True
            classes.extend(['feedback', 'weekly-feedback'])
            key = 'feedback'
        if 'course-feedback' in self.options:
            is_feedback = True
            classes.extend(['feedback', 'course-feedback-questionnaire'])
            key = 'feedback'
        if 'feedback' in self.options:
            is_feedback = True
            classes.extend('feedback')
            key = 'feedback'

        env = self.state.document.settings.env
        name = env.docname.replace('/', '_') + '_' + key

        env.questionnaire_is_feedback = is_feedback
        env.question_count = 0

        # Create document elements.
        node = aplus_nodes.html('div', {
            'class': ' '.join(classes),
            'data-aplus-exercise': 'yes',
            'data-aplus-quiz': 'yes',
        })
        form = aplus_nodes.html('form', {
            'action': key,
            'method': 'post',
        })
        nested_parse_with_titles(self.state, self.content, form)
        form.append(aplus_nodes.html('input', {
            'type': 'submit',
            'value': 'L&auml;het&auml;',
            'class': 'btn btn-primary',
        }))
        node.append(form)

        # Write configuration file.
        data = {
            'key': name,
            'category': category,
            'max_points': points,
            'feedback': is_feedback,
            'view_type': 'access.types.stdsync.createForm',
            'title|i18n': {
                'fi': 'Palaute',
                'en': 'Feedback',
            } if is_feedback else {
                'fi': u'Tehtävä ' + key,
                'en': 'Exercise ' + key,
            },
            'instructions': ('#!html', '<form[^>]*>(.*?)<div class="form-group'),
            'fieldgroups': [{
                'title': '',
                'fields': ('#!children', None),
            }],
        }
        node.write_yaml(env, name, data)
        toc_config.store_exercise(env, env.docname, data)
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

    def create_question(self):
        env = self.state.document.settings.env
        env.question_count += 1

        # Create document elements.
        node = aplus_nodes.html('div', {
            'class': ' '.join(self.get_classes()),
        })
        title = aplus_nodes.html('label', {})
        title.append(nodes.Text('Kysymys {:d}'.format(env.question_count)))
        node.append(title)

        # Add configuration data.
        data = {
            'type': self.grader_field_type(),
            'title': {
                'fi': 'Kysymys {:d}'.format(env.question_count),
                'en': 'Question {:d}'.format(env.question_count),
            },
        }
        if len(self.arguments) > 0:
            data['points'] = int(self.arguments[0])
        if 'required' in self.options:
            data['required'] = True
        node.set_yaml(data)

        return env, node, data

    def add_instructions(self, node, data, plain_content):
        if not plain_content:
            return

        parent = aplus_nodes.html('p', {'class':'help-block'})
        nested_parse_with_titles(self.state, plain_content, parent)
        node.append(parent)

        data['more'] = ('#!html', '<p class="help-block">(.*?)</p>')

    def add_feedback(self, node, data, paragraph):
        if not paragraph:
            return

        # Add feedback node for rendering without writing to file.
        data['feedback'] = ('#!children', 'feedback')
        feedbacks = aplus_nodes.html('p', {'class':'feedback-holder'}, no_write=True)

        for i,line in slicer(paragraph):
            if not '§' in line[0]:
                raise SphinxError('Feedback separator § exptected: {}'.format(line[0]))
            value,content = line[0].split('§', 1)
            value = value.strip()
            line[0] = content.strip()
            isnot = False
            if value.startswith('!'):
                isnot = True
                value = value[1:]

            # Create document elements.
            parent = nodes.paragraph()
            nested_parse_with_titles(self.state, line, parent)
            text = aplus_nodes.html('span', {'class':'text'})
            text.extend(parent.children)
            feedbacks.append(text)

            # Add configuration data.
            fbdata = {
                'value': value,
                'label': ('#!html', '<span class="text">(.*?)</span>'),
            }
            if isnot:
                fbdata['not'] = True
            text.set_yaml(fbdata, 'feedback')

        node.append(feedbacks)

    def get_classes(self):
        classes = ['form-group']
        if 'class' in self.options:
            classes.append(self.options['class'])
        return classes

    def grader_field_type(self):
        return 'undefined'


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
            if all('§' in line for line in last):
                feedback = last
                if len(empty_lines) > 1:
                    plain_content = self.content[:empty_lines[-2]]
                    choices = self.content[(empty_lines[-2] + 1):empty_lines[-1]]
                else:
                    choices = self.content[:empty_lines[-1]]
            else:
                choices = last
                plain_content = self.content[:empty_lines[-1]]
        else:
            choices = self.content

        # Create question.
        env, node, data = self.create_question()
        self.add_instructions(node, data, plain_content)
        data['options'] = ('#!children', 'option')

        # Travel all answer options.
        for i,line in slicer(choices):

            # Split choice key off.
            key,content = line[0].split(' ', 1)
            key = key.strip()
            line[0] = content.strip()

            # Trim the key.
            correct = False
            if key.startswith('*'):
                correct = True
                key = key[1:]
            if key.endswith('.'):
                key = key[:-1]

            # Create document elements.
            choice = aplus_nodes.html('div', {'class':'radio'})
            label = aplus_nodes.html('label', {})
            label.append(aplus_nodes.html('input', {
                'type': self.input_type(),
                'name': 'field_{:d}'.format(env.question_count - 1),
                'value': key,
            }))
            choice.append(label)
            node.append(choice)

            parent = nodes.paragraph()
            nested_parse_with_titles(self.state, line, parent)
            text = aplus_nodes.html('span', {'class':'text'})
            text.extend(parent.children)
            label.append(text)

            # Add configuration data.
            optdata = {
                'value': key,
                'label': ('#!html', '<span class="text">(.*?)</span>'),
            }
            if correct:
                optdata['correct'] = True
            choice.set_yaml(optdata, 'option')

        self.add_feedback(node, data, feedback)

        return [node]


class SingleChoice(Choice):
    ''' Lists options for picking the correct one. '''

    def form_group_class(self):
        return 'form-pick-one'

    def grader_field_type(self):
        return 'radio'

    def input_type(self):
        return 'radio'


class MultipleChoice(Choice):
    ''' Lists options for picking all the correct ones. '''

    def form_group_class(self):
        return 'form-pick-any'

    def grader_field_type(self):
        return 'checkbox'

    def input_type(self):
        return 'checkbox'


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
        position = 'place-on-own-line' if self.height > 1 or 'own-line' in self.options else 'place-inline'

        # Detect paragraphs: any number of plain content and correct answer including optional feedback
        plain_content = None
        config_content = []
        env = self.state.document.settings.env
        if env.questionnaire_is_feedback:
            plain_content = self.content
        else:
            empty_lines = list(loc for loc,line in enumerate(self.content) if line == u'')
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
            element = aplus_nodes.html('textarea', {
                'rows': self.height,
                'cols': self.length,
                'class': position,
            })
        else:
            element = aplus_nodes.html('input', {
                'type': 'text',
                'size': self.length,
                'class': position,
            })
        node.append(element)

        # Add configuration.
        if len(self.arguments) > 1:
            data['compare_method'] = self.arguments[1]
        if config_content:
            if '§' in config_content[0]:
                data['correct'] = config_content[0].split('§', 1)[0].strip()
            else:
                data['correct'] = config_content[0].strip()
                config_content = config_content[1:]
            self.add_feedback(node, data, config_content)

        return [node]

    def grader_field_type(self):
        return 'textarea' if self.height > 1 else 'text'

    def get_classes(self):
        classes = super().get_classes()
        if 'main-feedback' in self.options:
            classes.append('main-feedback-question')
        if 'required' in self.options:
            classes.append('required')
        else:
            classes.append('voluntary')
        if not 'no-standard-prompt' in self.options:
            classes.append('standard')
        if 'shorter-prompt' in self.options:
            classes.append('shorter')
        return classes
