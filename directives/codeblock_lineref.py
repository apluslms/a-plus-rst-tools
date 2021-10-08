# -*- coding: utf-8 -*-
'''
    Defines the directive lineref-code-block and role lref.

    lineref-code-block allows defining labels enclosed in :: for lines 
    of the code block. Labels can include alphanumeric characters, 
    underscore (_), and hyphen (-). Usage as with Sphinx directive code-block:

    .. lineref-code-block:: python
        :linenos:

        def example():
          :label-name:var = something
          return var

    The role lref makes it possible to link to labels defined in 
    lineref-code-block blocks:

    :lref:`optional link text <label-name>`
'''
import re

import docutils
from docutils import nodes
from docutils.parsers.rst import directives, roles

from sphinx.directives.code import CodeBlock
from sphinx.util import logging
from sphinx.locale import __

logger = logging.getLogger(__name__)

class codeblock_lineref(nodes.General, nodes.Element):
    pass

def visit_codeblock_lineref_node(self, node):
    # Pretty much copied from the codeblock visitor 
    # except for the addition of line anchors.
    lineanchors = node['lineanchor_id']
    node = node[0]
    lang = node.get('language', 'default')
    linenos = node.get('linenos', False)
    highlight_args = node.get('highlight_args', {})
    highlight_args['force'] = node.get('force', False)
    opts = self.config.highlight_options.get(lang, {})

    if linenos and self.config.html_codeblock_linenos_style:
        linenos = self.config.html_codeblock_linenos_style

    highlighted = self.highlighter.highlight_block(
        node.rawsource, lang, opts=opts, linenos=linenos, lineanchors=lineanchors,
        location=node, **highlight_args
    )
    starttag = self.starttag(node, 'div', suffix='',
                             CLASS='highlight-%s notranslate' % lang)
    self.body.append(starttag + highlighted + '</div>\n')
    raise nodes.SkipNode


def depart_codeblock_lineref_node(self, node):
    pass

def process_line(block, line, labelpattern, anchor):
    env = block.state.document.settings.env
    parts = re.split(r'(:[\w-]+:)', line) 
    newline = []
    for string in parts:
        if labelpattern.match(string):        
            label = string.strip(':')
            if label in env.code_line_labels:
                logger.warning(
                    __('Line reference labels should be unique: ' +
                          'label "{}" has already been defined'.format(label)), 
                    location=block.state_machine.get_source_and_line(
                        block.lineno)
                    )
                continue
            # Save the label and row numebr to env so that they are 
            # available later in visit_codeblock_lineref_node
            env.code_line_labels[label] = anchor
        elif string:
            # The processed line will include everything but the labels
            newline.append(string)
    return ('').join(newline)


class LineRefCodeBlock(CodeBlock):
    '''
    Directive for code blocks that can include line labels that 
    can be referenced to with the lref-role.
    '''

    def run(self):
        newlines = []
        env = self.state.document.settings.env
        # Random id for the code block is used in the line anchors
        randomid = str(env.new_serialno('lineref_codeblock'))
        labelpattern = re.compile(r':[\w-]+:')
        if not hasattr(env, 'code_line_labels'):
            env.code_line_labels = {}
        linecount = 0
        for line in self.content:
            linecount += 1
            anchor = randomid + '-' + str(linecount)
            newline = process_line(self, line, labelpattern, anchor)
            newlines.append(newline)
        self.content = newlines
        originals = CodeBlock.run(self)
        node = codeblock_lineref()
        node.extend(originals)
        node['lineanchor_id'] = randomid
        return [node]


def lineref_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Link to a line label in lineref-codeblock.

    Reference a label defined in a lineref-code-block.
    """

    env = inliner.document.settings.env
    location = (env.docname, lineno)

    linktext = text.partition('<')[0].strip()
    labelmatch = re.search(r'<([\w-]+)>', text)
    label = ''
    if not labelmatch:
        logger.warning(
            __('Missing label: the role lref requires a label and optional link text ' +
                  'in the form :lref:`link text <label>`'), 
            location=location
        )
        return [], []
    
    label = labelmatch.group(1)

    if not label in env.code_line_labels:
        logger.warning(
            __('Unknown label "{}"'.format(label)), 
            location=location
        )
        return [nodes.reference(rawtext, label, refuri='', **options)],[]


    anchor = env.code_line_labels[label]
    lineno = anchor.split('-')[1]
    parens = False
    if not linktext:
        # Default link text is (line X)
        linktext = 'line ' + lineno 
        parens = True
    linknode = nodes.reference(rawtext, str(linktext), refuri='#'+anchor, 
                                **options)
    linknode['classes'].append('codeblock-lineref')

    if parens:
        return [nodes.Text('('), linknode, nodes.Text(')')], []
    else:
         return [linknode], []


def setup(app):
    app.add_directive('lineref-code-block', LineRefCodeBlock)
    app.add_node(codeblock_lineref,
                 html=(visit_codeblock_lineref_node, depart_codeblock_lineref_node),
                 latex=(visit_codeblock_lineref_node, depart_codeblock_lineref_node),
                 text=(visit_codeblock_lineref_node, depart_codeblock_lineref_node))
    app.add_role('lref', lineref_role)
