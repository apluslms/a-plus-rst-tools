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
        'title': directives.unchanged, 
        'previous': directives.unchanged,
        'next': directives.unchanged, 
    }

    def run(self):
        self.assert_has_content()
        name = self.arguments[0]
        title_text = ''
        if 'title' in  self.options:
            title_text = self.options['title']

        node = nodes.container()
        title = nodes.container()
        content = nodes.container('\n'.join(self.content))
        nav = nodes.container()
        #rightnav = nodes.container()
        links = nodes.container()

        container_class = 'poi-container'
        node['classes'].extend(['poi']) # This style adds the border
        title['classes'].extend(['poi-title'])
        links['classes'].extend(['poi-links'])
        #rightnav['classes'].extend(['poi-rightnav'])
        content['classes'].extend([container_class, 'poi-content'])
        nav['classes'].extend([container_class])
        self.options['name'] = name
        self.add_name(node)
        options={}
        if 'previous' in self.options:
            label = nodes.Text('previous')
            prevlink = aplus_nodes.html(u'a', {u'href':u'#' + self.options['previous']})
            prevlink.append(label)
            links.append(prevlink)
        else:
            links.append(nodes.Text('previous'))
        links.append(nodes.Text(' | '))
        if 'next' in self.options:
            label = nodes.Text('next')
            nextlink = aplus_nodes.html(u'a', {u'href':u'#' + self.options['next']}, children=label)
            nextlink.append(label)
            links.append(nextlink)
        else:
            links.append(nodes.Text('next'))
        title.append(nodes.Text(title_text))
        nav.append(title)
        nav.append(links)
        #nav.append(rightnav)

        node.append(nav)
        node.append(content)

        # This might not work
        self.state.nested_parse(self.content, self.content_offset, content)

        return [node]

def setup(app):
    app.add_directive('point-of-interest', PointOfInterest)
