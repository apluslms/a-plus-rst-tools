'''
Directives that define automatically assessed questionnaires.
'''
from docutils.parsers.rst import directives
from docutils import nodes
from sphinx.errors import SphinxError
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
from directives.abstract_exercise import AbstractExercise
import aplus_nodes
import toc_config


class Questionnaire(AbstractExercise):
    ''' Wraps questionnaire configuration. '''
    has_content = True
    option_spec = {
        'chapter-feedback': directives.flag,
        'weekly-feedback': directives.flag,
        'course-feedback': directives.flag,
        'feedback': directives.flag,
        'submissions': directives.nonnegative_int,
        'points-to-pass': directives.nonnegative_int,
    }

    def run(self):
        self.assert_has_content()
        key, category, points = self.extract_exercise_arguments()

        # Parse options.
        classes = ['exercise']
        is_feedback = False
        if 'chapter-feedback' in self.options:
            classes.append('chapter-feedback')
            is_feedback = True
        if 'weekly-feedback' in self.options:
            classes.append('weekly-feedback')
            is_feedback = True
        if 'course-feedback' in self.options:
            classes.append('course-feedback-questionnaire')
            is_feedback = True
        if 'feedback' in self.options:
            is_feedback = True
        if is_feedback:
            key = 'feedback'
            category = category or 'feedback'
            classes.append('feedback')
        else:
            category = category or 'exercise'

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
        submit = aplus_nodes.html('input', {
            'type': 'submit',
            # TODO select by language
            'value': 'L&auml;het&auml;',
            'class': 'btn btn-primary',
        })
        form.append(submit)
        node.append(form)

        # Write configuration file.
        data = {
            'key': name,
            'category': category,
            'max_points': points,
            'max_submissions': self.options.get('submissions', env.config.questionnaire_default_submissions),
            'points_to_pass': self.options.get('points-to-pass', 0),
            'feedback': is_feedback,
            'view_type': 'access.types.stdsync.createForm',
            'title|i18n': {
                'fi': 'Palaute',
                'en': 'Feedback',
            } if is_feedback else {
                'fi': u'Tehtävä ' + key,
                'en': 'Exercise ' + key,
            },
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
        node = aplus_nodes.html('div', {
            'class': ' '.join(self.get_classes()),
        })
        data = {
            'type': self.grader_field_type(),
        }

        # Add title.
        if not title_text is None:
            data['title'] = title_text
        elif env.questionnaire_is_feedback:
            data['title'] = title_text = ''
        else:
            data['title|i18n'] = {
                'fi': 'Kysymys {:d}'.format(env.question_count),
                'en': 'Question {:d}'.format(env.question_count),
            }
            # TODO select by language
            title_text = data['title|i18n']['fi']
        if title_text:
            title = aplus_nodes.html('label', {})
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
            classes.extend(self.options['class'])
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


class AgreeGroup(Directive):
    ''' Groups agree items together. '''
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        # This directive is actually obsolete, AgreeItems can be placed alone.
        node = aplus_nodes.html('div', {'class':'agreement-group'})
        nested_parse_with_titles(self.state, self.content, node)
        return  [node]


class AgreeItem(QuestionMixin, Directive):
    ''' Question presenting an agreement scale. '''
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        option_texts = [
            { 'fi': 'täysin samaa mieltä', 'en': 'strongly agree' },
            { 'fi': 'jokseenkin samaa mieltä', 'en': 'agree' },
            { 'fi': 'jokseenkin eri mieltä', 'en': 'disagree' },
            { 'fi': 'täysin eri mieltä', 'en': 'strongly disagree' },
            { 'fi': 'en osaa sanoa / en kommentoi', 'en': 'cannot say / no comments' },
        ]

        # Create question and starndard options.
        env, node, data = self.create_question(title_text=self.arguments[0], points=False)
        options = []
        for i, label_text in enumerate(option_texts):

            options.append({
                'value': 4 - i,
                'label|i18n': label_text,
            })

            choice = aplus_nodes.html('div', {'class':'radio'})
            label = aplus_nodes.html('label', {})
            label.append(aplus_nodes.html('input', {
                'type': 'radio',
                'name': 'field_{:d}'.format(env.question_count - 1),
                'value': 4 - i,
            }))
            # TODO select by conf language
            label.append(nodes.Text(label_text['fi']))
            choice.append(label)
            node.append(choice)

        data['options'] = options
        return [node]

    def grader_field_type(self):
        return 'radio'
