# -*- coding: utf-8 -*-
import docutils
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from cgi import escape
import re

import aplus_nodes

# DIRECTIVE FOR REPL SESSIONS: repl
# this is an embarrassing mess, but it works for now. if you're thinking of making changes, rewrite instead.
# is there some better way to go about this by using inheritance from literal_block;
# and how are parsed literals represented as nodes, anyway?

class repl_node(nodes.line_block, nodes.Element): pass

class REPLSession(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec = { }

    def run(self):
        node = repl_node()
        node.content = self.content
        return [node]

def visit_repl_node(self, node):
    self.body.append('<pre class="repl literal-block">\n')

    previouslyInInputBlock = False
    for line in node.content:
        htmlLine = ""
        if line.startswith("> "):
            if previouslyInInputBlock:
                htmlLine += '\n'
            else:
                htmlLine += '<em>'
            htmlLine += escape(line[2:])
            previouslyInInputBlock = True
        elif line == "ø":                        # ø marks the non-output that the REPL provides when the result is Unit
            if previouslyInInputBlock:
                htmlLine += '</em>'
            previouslyInInputBlock = False
        else:
            def clean_output(line):
                line = escape(line)
                resStart = re.compile("^res((\d+)|X):")
                if re.match(resStart, line):
                    env = self.builder.env
                    line = resStart.sub("res" + str(env.repl_page_res_count) + ":", line)
                    env.repl_page_res_count += 1
                return line
            if previouslyInInputBlock:
                htmlLine += '</em>'
            if line.startswith("¡"):
                htmlLine += '<strong>'
                htmlLine += clean_output(line[1:])
                htmlLine += '</strong>'
            else:
                 htmlLine += clean_output(line)
            htmlLine += '\n'
            previouslyInInputBlock = False
        self.body += htmlLine

    if previouslyInInputBlock:
        self.body += '</em>'

def depart_repl_node(self, node):
    self.body.append("</pre>\n")

class res_count_reset_node(nodes.General, nodes.Element): pass

class ResCountReset(Directive):
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = { }

    def run(self):
        return [res_count_reset_node()]

def visit_res_count_reset_node(self, node):
    env = self.builder.env
    env.repl_page_res_count = 0

def depart_res_count_reset_node(self, node):
    pass


def setup(app):

    ignore_visitors = (aplus_nodes.visit_ignore, aplus_nodes.depart_ignore)

    app.add_node(repl_node, html=(visit_repl_node, depart_repl_node),
            latex=ignore_visitors)
    app.add_directive('repl', REPLSession)

    app.add_node(res_count_reset_node, html=(visit_res_count_reset_node, depart_res_count_reset_node),
            latex=ignore_visitors)
    app.add_directive('repl-res-count-reset', ResCountReset)


