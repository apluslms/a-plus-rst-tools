# -*- coding: utf-8 -*-
'''
Directive for creating "point of interest" summary block.

.. point-of-interest:: name (unique id within the document)
    :title: optional title text
    :previous: name of previous point-of-interest
    :next: name of next point-of-interest
    :hidden: (if this flag is present, the content of this poi is hidden by default)

    Content of point-of-interest here

'''
import os.path
from docutils.parsers.rst import directives
from docutils import nodes
from sphinx.util.compat import Directive

import aplus_nodes


class PointOfInterest(Directive):
    required_arguments = 1
    has_content = True
    final_argument_whitespace = True
    option_spec = {
        'title': directives.unchanged, 
        'previous': directives.unchanged,
        'next': directives.unchanged, 
        'hidden': directives.flag,
        'class' : directives.class_option,
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
        links = nodes.container()

        container_class = 'poi-container'
        node['classes'].extend(['poi']) 
        if 'class' in self.options:
            node['classes'].extend(self.options['class'])
        title['classes'].extend(['poi-title'])
        links['classes'].extend(['poi-links'])
        content['classes'].extend([container_class, 'poi-content', 'collapse'])
        if not 'hidden' in self.options:
            content['classes'].extend(['in'])
        nav['classes'].extend([container_class])

        self.options['name'] = name
        self.add_name(node)
        # There may be a better way to add id to the content node
        content_name = name + '-content'
        self.options['name'] = content_name
        self.add_name(content)

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
            nextlink = aplus_nodes.html(u'a', {u'href':u'#' + self.options['next']})
            nextlink.append(label)
            links.append(nextlink)
        else:
            links.append(nodes.Text('next'))

        icon = aplus_nodes.html(u'img', {
            u'src':u'../_static/poi.png', 
            u'alt':u'Point of interest icon',
            u'class':u'poi-icon',
            })

        hidelink = aplus_nodes.html(u'a', {
            u'href':u'#' + content_name, 
            u'data-toggle':u'collapse'})

        hidelink.append(icon)
        hidelink.append(nodes.Text(title_text))
        title.append(hidelink)
        nav.append(title)
        nav.append(links)

        node.append(nav)
        node.append(content)

        self.state.nested_parse(self.content, self.content_offset, content)

        return [node]

def setup(app):
    app.add_directive('point-of-interest', PointOfInterest)
