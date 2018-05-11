# -*- coding: utf-8 -*-
'''
Directive for creating "point of interest" summary block.

.. point-of-interest:: name
    :previous:
    :next:

'''
import os.path
from docutils.parsers.rst import directives
from docutils import nodes

import aplus_nodes

from sphinx.util.compat import Directive


class PointOfInterest(Directive):
    required_arguments = 1
    has_content = True
    final_argument_whitespace = True
    option_spec = {
        'previous': directives.unchanged,
        'next': directives.unchanged, 
    }

    def run(self):
        self.assert_has_content()
        name = self.arguments[0]

        '''
        # TODO: 

        nodes:

        node    - container with class poi and id name
        content - container for actual content
        nav     - container for prev/next links
        leftnav - container for prev link
        rightnav- container for next link
        prev    - link to poi named in previous option
        next    - link to poi named in next

        '''
        node = nodes.container()
        content = nodes.container('\n'.join(self.content))
        nav = nodes.container()
        rightnav = nodes.container()
        leftnav = nodes.container()

        container_class = 'poi-container'
        node['classes'].extend(['poi'])
        leftnav['classes'].extend(['poi-leftnav'])
        rightnav['classes'].extend(['poi-rightnav'])
        content['classes'].extend([container_class])
        nav['classes'].extend([container_class])
        self.options['name'] = name
        self.add_name(node)
        options={}
        if 'previous' in self.options:
            label = nodes.Text('previous')
            prevlink = aplus_nodes.html(u'a', {u'href':u'#' + self.options['previous']})
            prevlink.append(label)
            leftnav.append(prevlink)
        if 'next' in self.options:
            label = nodes.Text('next')
            nextlink = aplus_nodes.html(u'a', {u'href':u'#' + self.options['next']}, children=label)
            nextlink.append(label)
            rightnav.append(nextlink)

        nav.append(leftnav)
        nav.append(rightnav)

        node.append(content)
        node.append(nav)

        # This might not work
        self.state.nested_parse(self.content, self.content_offset, content)

        return [node]

def setup(app):
    app.add_directive('point-of-interest', PointOfInterest)
