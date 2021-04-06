# This implementation is based on the sphinxcontrib-contentui repository:
# https://github.com/ulrobix/sphinxcontrib-contentui/
# -*- coding: utf-8 -*-
"""
Tabs
====

Directive for creating tabs.

.. rst-tabs::

  .. tab-content:: tab1
    :title: Tab title one

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus hendrerit 
    auctor quam at maximus. Phasellus ornare suscipit tortor et aliquet. Aliquam 
    erat volutpat. Aliquam at orci vel nibh tincidunt lacinia. Cras gravida, 
    mauris eget vulputate ullamcorper, turpis est commodo velit, consequat 
    pulvinar augue mi malesuada metus. Maecenas ac diam et augue placerat 
    faucibus. Nullam ut iaculis nisi.

  .. tab-content:: tab2
    :title: Tab title two

    .. code-block:: rst
    
      Insert Your Code here.
"""
import os
from docutils.parsers.rst import Directive, directives
from docutils import nodes
from docutils.statemachine import StringList
from sphinx.util.fileutil import copy_asset
from sphinx.util import logging

import aplus_nodes

CSS_FILE = 'css/aplus_tab.css'
JS_FILE = 'js/aplus_tab.js'

assets_path = 'static'

logger = logging.getLogger(__name__)


class NavTabDirective(Directive):
    has_content = True
    optional_arguments = 1

    def run(self):
        self.assert_has_content()
        text = '\n'.join(self.content)
        node = nodes.container(text)
        node['classes'].append('rst-tabs')

        if self.arguments and self.arguments[0]:
            node['classes'].append(self.arguments[0])

        self.add_name(node)
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class TabContentDirective(Directive):
    has_content = True
    option_spec = {'title': directives.unchanged}
    required_arguments = 1

    def run(self):
        self.assert_has_content()
        text = '\n'.join(self.content)
        node = nodes.container(text)
        node['ids'].append('tab-%s' % self.arguments[0])
        node['classes'].append('tab-content')

        par = nodes.paragraph(text=self.options["title"])
        par['classes'].append('tab-title')
        node += par

        self.add_name(node)
        self.state.nested_parse(self.content, self.content_offset, node)

        return [node]

def add_assets(app):
    # This method reads the `include_annotated_css` and `include_annotated_js`
    # settings from the conf.py file located in the course directory. If such
    # settings are not found, the default settings defined in the setup()
    #  method will be used instead
    app.config.include_tab_css and app.add_css_file(CSS_FILE)
    app.config.include_tab_js and app.add_js_file(JS_FILE)


def copy_asset_files(app, exception):
    if exception:
        return

        
    # The files are added to the _build/html/_static/css folder.
    if app.config.include_tab_css:
        logger.info('Copying CSS files from the tabs directive to the _static folder... ')
        html_static_path_css = os.path.join(assets_path, CSS_FILE)
        local_path_css = os.path.join(os.path.dirname(__file__), html_static_path_css)
        copy_asset(local_path_css, os.path.join(app.outdir, '_static', 'css'))
        logger.info('done')

    # The files are added to the _build/html/_static/js folder.
    if app.config.include_tab_js:
        logger.info(
        'Copying JS files from the annotated directive to the _static folder... ')
        html_static_path_js = os.path.join(assets_path, JS_FILE)
        local_path_js = os.path.join(os.path.dirname(__file__), html_static_path_js)
        copy_asset(local_path_js, os.path.join(app.outdir, '_static', 'js'))
        logger.info('done')


def setup(app):

    app.add_config_value('include_tab_css', True, 'html')
    app.add_config_value('include_tab_js', True, 'html')

    app.add_directive('rst-tabs',  NavTabDirective)
    app.add_directive('tab-content', TabContentDirective)

    app.connect('builder-inited', add_assets)
    app.connect('build-finished', copy_asset_files)
