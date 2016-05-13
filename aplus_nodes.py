from docutils import nodes
import yaml_writer


class html(nodes.General, nodes.Element):

    def __init__(self, tagname, attributes):
        self.tagname = tagname
        super().__init__(rawsource='', **attributes)

    def has_yaml_data(self):
        return hasattr(self, 'yaml_data')


def visit_html(self, node):
    self.body.append(node.starttag())


def depart_html(self, node):
    self.body.append(node.endtag())
    if hasattr(node, 'yaml_data'):
        node.yaml_data.write()
