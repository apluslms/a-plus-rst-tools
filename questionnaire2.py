'''
Adds support for directives that define automatically assessed questionnaires.
'''
from docutils.parsers.rst import directives
from docutils import nodes
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
import yaml_writer
import aplus_nodes


def docname(env):
    return env.docname.replace('/', '_')


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
    }

    def run(self):
        self.assert_has_content()

        #node['chapter-feedback'] = 'chapter-feedback' in self.options
        #node['weekly-feedback']  = 'weekly-feedback' in self.options
        #node['course-feedback']  = 'course-feedback' in self.options

        # if not env.questionnaire_is_feedback:
        #     if len(self.arguments) < 2:
        #         return [self.state.document.reporter.error('Missing arguments (id and/or points) in questionnaire:\n' + self.block_text)]
        #     node['exercise_number'] = self.arguments[0]
        #     node['points'] = self.arguments[1]
        #
        #     (source, line) = self.state.state_machine.get_source_and_line()
        #     node['src'] = env.srcdir
        #     # ugly way to get a relative path
        #     #path_snippet = str(source)[len(env.srcdir) + 2:]
        #     #node['k00_chapter_num'] = int(path_snippet[0:2])


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

        #for e in form.children:

        # Record configuration.
        data = {
            'title': '',
            'description': '',
            'max_points': 0,
            'view_type': 'access.types.stdsync.createForm',
            'fieldgroups': [{
                'title': '',
                'fields': [],
            }],
        }
        env = self.state.document.settings.env
        node.write_yaml(env, docname(env), data)

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


def setup(app):
    app.connect('builder-inited', yaml_writer.create_directory)
    app.add_node(
        aplus_nodes.html,
        html=(aplus_nodes.visit_html, aplus_nodes.depart_html)
    )
    app.add_directive('questionnaire', Questionnaire)
    app.add_directive('pick-one', SingleChoice)
    #app.add_directive('pick-any',  MultipleChoice)
    #app.add_directive('freetext',  FreeText)
    #app.add_directive('agree-group',  AgreeGroup)
    #app.add_directive('agree-item',  AgreeItem)
