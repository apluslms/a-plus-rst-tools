# -*- coding: utf-8 -*-
'''
Directive for creating "point of interest" summary block.

.. point-of-interest:: name (unique id within the document)
    :title: optional title text
    :previous: name of previous point-of-interest
    :next: name of next point-of-interest
    :hidden: (if this flag is present, the content of this poi is hidden by default)
    :class: any additional css classes

    Content of point-of-interest here

'''
import os.path
from docutils.parsers.rst import directives
from docutils import nodes
from sphinx.util.compat import Directive
from sphinx.errors import SphinxError
from sphinx.util import logging

import aplus_nodes

logger = logging.getLogger(__name__)


class poi_nav(nodes.General, nodes.Element):
    pass


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
        if len(self.arguments) == 0:
            return [nodes.container()]
        name = self.arguments[0]
        title_text = ''
        if 'title' in  self.options:
            title_text = self.options['title']

        node = nodes.container()
        title = nodes.container()
        content = nodes.container('\n'.join(self.content))
        nav = nodes.container()
        links = nodes.container()
        # poi_nav node is later replaced by reference nodes which
        # need to be within a TextElement-node
        text = nodes.inline()
        poinav = poi_nav()
        # poinav id needs to be added so that we can identify the node later when processing
        poinav['ids'].append(name)

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
        content_name = name + '-content'
        content['ids'].append(content_name)

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
        text.append(poinav)
        links.append(text)
        nav.append(links)

        node.append(nav)
        node.append(content)

        self.state.nested_parse(self.content, self.content_offset, content)

        # poi_info needs to be stored to env to be able to construct the
        # refuris later
        env = self.state.document.settings.env
        poi_info = {
            'docname': env.docname,
        }
        if 'previous' in self.options:
            poi_info['previous'] = self.options['previous']
        if 'next' in self.options:
            poi_info['next'] = self.options['next']

        if not hasattr(env, 'poi_all'):
            env.poi_all = {}
        env.poi_all[name] = poi_info

        return [node]


def process_poi_nodes(app, doctree, fromdocname):

    # Add links to next and previous point of interest nodes
    env = app.builder.env

    def make_refnode(node, target_name):
        newnode = nodes.reference('', '')
        if target_name in env.poi_all:
            target_info = env.poi_all[target_name]
            newnode['refdocname'] = target_info['docname']
            if fromdocname != target_info['docname']:
                newnode['refuri'] = app.builder.get_relative_uri(
                    fromdocname, target_info['docname'])
                newnode['refuri'] += '#' + target_name
        else:
            logger.warning('Reference to an unknown point of interest "{}".'.format(target_name), location=node)
        if not 'refuri' in newnode:
            newnode['refuri'] = '#' + target_name
        return newnode

    for node in doctree.traverse(poi_nav):
        content = []
        name = node['ids'][0]
        node['ids'] = []
        poi_info = env.poi_all[name]
        label_previous = nodes.Text('previous')
        label_next = nodes.Text('next')
        if 'previous' in poi_info:
            previous_name = poi_info['previous']
            refnode = make_refnode(node, previous_name)
            refnode.append(label_previous)
            content.append(refnode)
        else:
            content.append(label_previous)
        content.append(nodes.Text(' | '))
        if 'next' in poi_info:
            next_name = poi_info['next']
            refnode = make_refnode(node, next_name)
            refnode.append(label_next)
            content.append(refnode)
        else:
            content.append(label_next)

        node.replace_self(content)



def setup(app):
    app.add_directive('point-of-interest', PointOfInterest)
    app.add_node(poi_nav)

    app.connect('doctree-resolved', process_poi_nodes)