import os.path
import re
from docutils import nodes

import lib.yaml_writer as yaml_writer
import lib.html_tools as html_tools


class html(nodes.General, nodes.Element):
    '''
    Represents HTML tags that have name and attributes. In addition, nodes can
    store configuration data. Some configurations include HTML rendered from
    RST so the configuration processing and writing is delayed. Configuration
    data can include following field values that will be transformed.

    "some_key": ("#!children", "data_type")
        Collects configuration from children nodes into a list.
        The type is used to filter the children. None type includes all
        children data and HTML representations of alien children nodes.

    "some_key": ("#!html", 'by_name')
        Captures rendered HTML from children nodes that were requested
        to store HTML.
    '''

    def __init__(self, tagname, attributes={}, no_write=False, skip_html=False, *children, **other_attributes):
        ''' Constructor: no_write option removes node from final document after configuration data is processed. '''
        self.tagname = tagname
        self.no_write = no_write
        self.skip_html = skip_html
        attrs = other_attributes.copy()
        attrs.update(attributes) # attributes dict gets prioritized if the same key exists in both dicts
        super(html, self).__init__("", *children, **attrs)

    def write_yaml(self, env, name, data_dict, data_type=None):
        ''' Adds configuration data and requests write into a file. '''
        self.set_yaml(data_dict, data_type)
        self.yaml_write = yaml_writer.file_path(env, name)

    def set_yaml(self, data_dict, data_type=None):
        ''' Adds configuration data. '''
        self.yaml_data = data_dict
        if data_type:
            self.yaml_data['_type'] = data_type

    def has_yaml(self, data_type=None):
        if hasattr(self, 'yaml_data'):
            types = data_type if isinstance(data_type, list) else [data_type]
            if not data_type or ('_type' in self.yaml_data and self.yaml_data['_type'] in types):
                return True
        return False

    def pop_yaml(self):
        data = self.yaml_data
        if '_type' in data:
            del data['_type']
        del self.yaml_data
        return data

    def store_html(self, name):
        self.html_extract = name

    def copy(self):
        '''sphinx.util.nodes (function _new_copy) monkey-patches the Element.copy method
        to include the source and line, however, it calls the Element constructor with
        a positional argument rawsource instead of using keyword arguments.
        That is changed here so that the constructor of this class can use other
        positional parameters.
        '''
        newnode = self.__class__(self.tagname, self.attributes, self.no_write,
            self.skip_html, *self.children)
        if isinstance(self, nodes.Element):
            newnode.source = self.source
            newnode.line = self.line
        return newnode


def collect_data(body, node, data_type=None):
    data = []

    def add_static_block(from_body, last_body):
        if data_type is None and last_body > from_body:
            data.append({
                'type': 'static',
                'title': "",
                'more': "".join(body[from_body:last_body]),
            })

    def recursive_collect(parent, from_body):
        body_i = from_body
        for child in parent.children:
            if hasattr(child, 'has_yaml'):
                yaml = child.has_yaml(data_type)
                if yaml or child.skip_html:
                    add_static_block(body_i, child._body_begin)
                    body_i = child._body_end
                if yaml:
                    data.append(child.pop_yaml())
            body_i = recursive_collect(child, body_i)
        return body_i

    if node.children:
        from_body = recursive_collect(node, node._body_children_begin)
        add_static_block(from_body, node._body_children_end)
    return data


def collect_html(node, name):
    html = []
    for n in node.children:
        if hasattr(n, 'html_extract') and n.html_extract == name:
            html.append(n._html)
        html.append(collect_html(n, name))
    return "".join(html)


def recursive_fill(body, data_dict, node):
    for key,val in data_dict.items():
        if isinstance(val, tuple):
            if val[0] == '#!children':
                data_dict[key] = collect_data(body, node, val[1])
            elif val[0] == '#!html':
                data_dict[key] = collect_html(node, val[1])
        elif isinstance(data_dict[key], dict):
            recursive_fill(body, data_dict[key], node)
        elif isinstance(data_dict[key], list):
            for a_dict in [a for a in data_dict[key] if isinstance(a, dict)]:
                recursive_fill(body, a_dict, node)


def visit_html(self, node):
    ''' The HTML render begins for the node. '''
    if node.no_write:
        node._real_body = self.body
        self.body = []
    node._body_begin = len(self.body)
    self.body.append(node.starttag())
    node._body_children_begin = len(self.body)


p_tag_start = re.compile(r'<p>')
p_tag_end   = re.compile(r'</p>\s*')

def depart_html(self, node):
    ''' The HTML render ends for the node. '''
    node._body_children_end = len(self.body)
    self.body.append(node.endtag())
    node._body_end = len(self.body)
    if hasattr(node, 'html_extract'):
        node._html = "".join(self.body[(node._body_begin+1):-1])
        # Remove <p> elements from inside choice labels and question hints.
        # They occur in questionnaires. HTML <label> may not contain <p> and
        # the hints are inserted to a template that already wraps them in <p>.
        if node.html_extract in ['hint', 'label']:
            node._html = p_tag_end.sub('', p_tag_start.sub('', node._html))
    if hasattr(node, 'yaml_data'):
        recursive_fill(self.body, node.yaml_data, node)
        if hasattr(node, 'yaml_write'):
            yaml_writer.write(node.yaml_write, node.pop_yaml())
    if node.no_write:
        self.body = node._real_body


class aplusmeta(nodes.General, nodes.Element):
    ''' Hidden node that includes meta data. '''

    def __init__(self, options={}, *children, **attributes):
        assert len(children) == 0, "aplusmeta node may not have children"
        self.options = options
        super(aplusmeta, self).__init__(rawsource="", **attributes)

    def copy(self):
        '''sphinx.util.nodes (function _new_copy) monkey-patches the Element.copy method
        to include the source and line, however, it calls the Element constructor with
        a positional argument rawsource instead of using keyword arguments.
        That is changed here so that the constructor of this class can use other
        positional parameters.
        '''
        newnode = self.__class__(self.options, *self.children, **self.attributes)
        if isinstance(self, nodes.Element):
            newnode.source = self.source
            newnode.line = self.line
        return newnode


def visit_ignore(self, node):
    pass


def depart_ignore(self, node):
    pass
