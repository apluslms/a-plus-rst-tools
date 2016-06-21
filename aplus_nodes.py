import os.path
import re
from docutils import nodes

import yaml_writer


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

    "some_key": ("#!html", "<p>(.*?)</p>")
        Matches and captures rendered HTML from the rendered node.
        The second part is a Python regexp.
    '''

    def __init__(self, tagname, attributes={}, no_write=False):
        ''' Constructor: no_write option removes node from final document after configuration data is processed. '''
        self.tagname = tagname
        self.no_write = no_write
        super().__init__(rawsource='', **attributes)

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


def collect(body, node, data_type=None):
    data = []
    e = 0
    for i in range(len(node.children)):
        child = node.children[i]

        def recursive_collect(n):
            if hasattr(n, 'has_yaml'):
                if n.has_yaml(data_type):
                    data.append(n.pop_yaml())
            for c in n.children:
                recursive_collect(c)
        recursive_collect(child)

        # Collect body for non data nodes.
        if not data_type and not hasattr(child, 'has_yaml'):
            b = i - 1
            while b >= 0 and not hasattr(node.children[b], '_body_end'):
                b -= 1
            b = node.children[b]._body_end if b >= 0 else (node._body_begin + 1)

            if b >= e:
                e = i + 1
                while e < len(node.children) and not hasattr(node.children[e], '_body_begin'):
                    e += 1
                e = node.children[e]._body_begin if e < len(node.children) else (node._body_end - 1)
                data.append({
                    'type': 'static',
                    'title': '',
                    'more': ''.join(body[b:e]),
                })
    return data


def recursive_fill(body, data_dict, node):
    for key,val in data_dict.items():
        if isinstance(val, tuple):
            if val[0] == '#!children':
                data_dict[key] = collect(body, node, val[1])
            elif val[0] == '#!html':
                res = re.findall(val[1], ''.join(body[node._body_begin:]), re.DOTALL)
                data_dict[key] = res[0] if len(res) > 0 else ''
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


def depart_html(self, node):
    ''' The HTML render ends for the node. '''
    self.body.append(node.endtag())
    node._body_end = len(self.body)
    if hasattr(node, 'yaml_data'):
        recursive_fill(self.body, node.yaml_data, node)
        if hasattr(node, 'yaml_write'):
            yaml_writer.write(node.yaml_write, node.pop_yaml())
    if node.no_write:
        self.body = node._real_body
