'''
Adds support for directives that define automatically assessed questionnaires.
'''
from docutils.parsers.rst import directives
from docutils import nodes
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
import itertools
import aplus_nodes
import yaml_writer


def get_doc_name(env):
    return env.docname.replace('/', '_')


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
    '''
    Wraps questionnaire configuration.
    '''
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
        is_feedback = 'chapter-feedback' in self.options or 'weekly-feedback' in self.options or 'course-feedback' in self.options or 'feedback' in self.options
        if is_feedback:
            key = 'feedback'

        env = self.state.document.settings.env
        doc_name = get_doc_name(env)
        name = doc_name + '_' + key

        # Create element.
        node = aplus_nodes.html('div', {
            'class': 'exercise',
            'data-aplus-exercise': 'yes',
            'data-aplus-quiz': 'yes',
        })
        form = aplus_nodes.html('form', {
            'action': '',
            'method': 'post',
        })
        node.append(form)
        nested_parse_with_titles(self.state, self.content, form)

        # Write configuration file.
        data = {
            'key': name,
            'title|i18n': {
                'fi': 'Palaute',
                'en': 'Feedback',
            } if is_feedback else {
                'fi': 'Tehtävä ' + key,
                'en': 'Exercise ' + key,
            },
            'description': '',
            'feedback': is_feedback,
            'max_points': points,
            'view_type': 'access.types.stdsync.createForm',
            'fieldgroups': [{
                'title': '',
                'fields': [e.yaml_data for e in form.children if e.has_yaml_data()],
            }],
        }
        yaml_writer.write(env, name, data)

        # Store same data in environment.
        if not doc_name in env.aplus['exercises']:
            env.aplus['exercises'][doc_name] = []
        env.aplus['exercises'][doc_name].append(data)

        return [node]


class SingleChoice(Directive):
    '''
    Lists options for picking the correct one.
    '''
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        'class' : directives.class_option
    }

    def run(self):
        node = aplus_nodes.html('div', {
            'class': 'pick-one'
        })
        return [node]
