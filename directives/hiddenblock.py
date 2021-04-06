# -*- coding: utf-8 -*-
'''
Directive for creating hidden content blocks.

.. hidden-block:: name-required
  :label: Optional text for the show/hide link (default Show/Hide)
  :visible: # if this flag is present, the collapsible div starts out visible

  hidden content here 

'''
import os.path
from docutils.parsers.rst import Directive, directives
from docutils import nodes

import aplus_nodes


class HiddenBlock(Directive):
    required_arguments = 1
    has_content = True
    final_argument_whitespace = True
    option_spec = {
        'label': directives.unchanged,
        'visible': directives.flag 
    }

    def run(self):
        self.assert_has_content()
        node = nodes.container()
        name = self.arguments[0]
        # TODO: maybe use sphinx/docutils node instead of aplus_node for the link
        link = aplus_nodes.html('a', {
            'href':'#' + name, 
            'data-toggle':'collapse'})
        label = 'Show/Hide'
        if 'label' in self.options:
            label = self.options['label']

        # Container for the hidden content
        classes = ['collapse']
        if 'visible' in self.options:
            classes.append('in')
        collapsible = nodes.container('\n'.join(self.content))
        collapsible['classes'].extend(classes)
        self.options['name'] = name
        self.add_name(collapsible)

        link.append(nodes.Text(label))
        node.append(link)
        node.append(collapsible)
        self.state.nested_parse(self.content, self.content_offset, collapsible)

        return [node]
