# -*- coding: utf-8 -*-
'''
Directive for creating "point of interest" summary block.

.. point-of-interest:: title text
    :id: unique id within the document
    :previous: name of previous point-of-interest
    :next: name of next point-of-interest
    :hidden: (if this flag is present, the content of this poi is hidden by default)
    :class: any additional css classes
    :height: optional fixed height for content
    :columns: relative widths of poi content columns (e.e. 2 3 3) DEPRECATED, this is used with ::newcol
    :bgimage: path to background image
    :not_in_slides: used with the presentation maker. This POI does not show in the slides when used.
    :not_in_book: This POI does not appear in the book material when used
    :no_poi_box: Removes surrounding box and navigation

    Content of point-of-interest here


'''
import os.path, random, string
from math import floor
from docutils.parsers.rst import Directive, directives
from docutils import nodes
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
        'id': directives.unchanged,
        'title': directives.unchanged,
        'previous': directives.unchanged,
        'next': directives.unchanged,
        'hidden': directives.flag,
        'class' : directives.class_option,
        'height': directives.length_or_percentage_or_unitless,
        'columns': directives.unchanged,
        'bgimg':directives.uri,
        # not_in_slides and not_in_book are used with the presentation maker
        'not_in_slides': directives.flag,
        'not_in_book': directives.flag,
        'no_poi_box': directives.flag,
    }

    def run(self):
        self.assert_has_content()
        env = self.state.document.settings.env
        if not hasattr(env, 'poi_all'):
            env.poi_all = {}
        if len(self.arguments) == 0:
            return [nodes.container()]

        if 'title' in self.options:
            if 'id' in self.options:
                raise SphinxError('Point of interest options can\'t contain both "title" and "id"; one of them should be provided as an argument instead')
            name = self.arguments[0]
            title_text = self.options['title']
        else:
            name = self.options.get('id')
            if not name:
                choices = string.ascii_lowercase + string.digits
                while True:
                    name = ''.join(random.choice(choices) for i in range(6))
                    if name not in env.poi_all:
                        break
            title_text = self.arguments[0]

        node = nodes.container()
        title = nodes.container()

        if 'not_in_book' in self.options:
            # Ignore this point of interest in the output since it shall not be
            # included in the A+ course materials (e-book).
            return []

        if 'no_poi_box' not in self.options:
            container_class = 'poi-container'
            content_name = name + '-content'

            # add an extra div to force content to desired height
            hcontainer_opts = {
                'style': 'height:' + self.options.get('height', '') + ';',
                'class': container_class + ' poi-content row',
            }
        else:
            container_class = 'no-poi-box'
            content_name = name
            hcontainer_opts = {
                'style': 'height:' + self.options.get('height', '') + ';',
                'class': 'row',
            }

        if 'bgimg' in self.options:
            static_host = os.environ.get('STATIC_CONTENT_HOST', None)
            if not static_host:
                logger.warning('Environment variable STATIC_CONTENT_HOST must be set to be able to use point of interest background', location=node)
            else:
                docname = env.docname
                imgname = self.options['bgimg'].split('/')[-1]
                imgpath = ('/').join(docname.split('/')[0:-1]) + '/' + self.options['bgimg']
                urlstring = 'background-image:url(' + static_host + '/_images/' + imgname + ');'
                hcontainer_opts['style'] = hcontainer_opts['style'] + urlstring
                # Add background image to env and builder so that it will
                # be correctly copied to static _images build directory
                env.images[imgpath] = ({docname}, imgname)
                env.app.builder.images[imgpath] = imgname

        hcontainer = aplus_nodes.html('div', hcontainer_opts)
        collapsible = nodes.container()

        contentnodes = []
        colseparator = '::newcol'
        colcontent = ''
        colcontent_l = []
        colwidths = None
        prevl = 0
        l = 0
        if 'columns' in self.options:
            cols = list(map(int,self.options['columns'].split()))
            allcols = sum(cols)
            colwidths = [x / allcols for x in cols]

        for batch in self.content:
            l += 1
            if batch == colseparator:
                cn = len(contentnodes)
                cwidth = None
                if colwidths:
                    cwidth = floor(colwidths[cn] * 12)
                cnode = nodes.container(colcontent)
                hcontainer.append(cnode)
                contentnodes.append((self.content[prevl:l-1], self.content_offset + prevl, cnode, cwidth))

                colcontent = ''
                prevl = l
            else:
                colcontent_l.append(batch)
                colcontent += batch
                colcontent += '\n'

        # add last column
        cnode = nodes.container(colcontent)
        hcontainer.append(cnode)
        cwidth = None
        if colwidths:
            cwidth = floor(colwidths[-1] * 12)
        contentnodes.append((self.content[prevl:], self.content_offset + prevl, cnode, cwidth))

        nav = nodes.container()
        links = nodes.container()
        # poi_nav node is later replaced by reference nodes which
        # need to be within a TextElement-node
        text = nodes.inline()
        poinav = poi_nav()
        # Create a relative path to the _build/html/_static/poi.png file
        # from the built HTML file of the current RST document.
        dir_depth = len(os.path.dirname(env.doc2path(env.docname, None)).split(os.path.sep))
        icon = aplus_nodes.html('img', {
            'src': ('../' * dir_depth) + '_static/poi.png',
            'alt': 'Point of interest icon',
            'class': 'poi-icon',
        })
        hidelink = aplus_nodes.html('a', {
            'href':'#' + content_name,
            'data-toggle':'collapse'})
        hidelink.append(icon)

        if ":math:" in title_text:
            math_eq = title_text.split('`')[1]
            math_node = nodes.math()
            math_node['latex'] = math_eq
            hidelink.append(math_node)
            title.append(hidelink)
            nav.append(title)
        else:
            hidelink.append(nodes.Text(title_text))
            title.append(hidelink)
            nav.append(title)
        text.append(poinav)
        links.append(text)
        nav.append(links)

        if 'no_poi_box' not in self.options:
            node.append(nav)

        node.append(collapsible)
        collapsible.append(hcontainer)

        numcols = len(contentnodes)
        for cont, offset, cnode, cwidth in contentnodes:
            # Bootstrap uses 12 unit grid
            if not cwidth:
                cwidth = int(12 / numcols)
            cnode['classes'] = ['col-sm-' + str(cwidth)]
            self.state.nested_parse(cont, offset, cnode, hcontainer)

        # poinav id needs to be added so that we can identify the node later when processing
        poinav['ids'].append(name)

        self.options['name'] = name
        self.add_name(node)
        collapsible['ids'].append(content_name)
        collapsible['classes'].extend([container_class, 'collapse'])
        node['classes'].extend(['poi'])
        if 'class' in self.options:
            node['classes'].extend(self.options['class'])
        title['classes'].extend(['poi-title'])
        links['classes'].extend(['poi-links'])

        if not 'hidden' in self.options:
            collapsible['classes'].extend(['in'])
        nav['classes'].extend([container_class])

        # poi_info needs to be stored to env to be able to construct the
        # refuris later
        poi_info = {
            'docname': env.docname,
        }
        if 'previous' in self.options:
            poi_info['previous'] = self.options['previous']
        if 'next' in self.options:
            poi_info['next'] = self.options['next']

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


def purge_pois(app, env, docname):
    if not hasattr(env, 'poi_all'):
        return

    env.poi_all = {poi_id:poi for poi_id, poi in env.poi_all.items()
                          if poi['docname'] != docname}


def setup(app):
    app.add_directive('point-of-interest', PointOfInterest)
    app.add_node(poi_nav)

    app.connect('doctree-resolved', process_poi_nodes)
    app.connect('env-purge-doc', purge_pois)
