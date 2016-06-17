'''
Directive that places exercise submission forms.
'''
from docutils import nodes
from sphinx.util.compat import Directive
import aplus_nodes


class SubmitForm(Directive):
    has_content = False
    required_arguments = 2
    optional_arguments = 0
    option_spec = {

    }

    def run(self):
        node['exercise_number'] = self.arguments[0]
        node['points'] = self.arguments[1]

        classes = []
        node = aplus_nodes.html('div', {
            'class': ' '.join(classes),
            'data-aplus-exercise': 'yes',
        })
        return [node]

def visit_submit_node(self, node):
    self.body.append('<div class="submit-exercise" data-id="%s" points="%s">' % (node['exercise_number'],node['points']))

def depart_submit_node(self, node):
    self.body.append("</div>\n")
