# -*- coding: utf-8 -*-
'''
This directive can be used to insert basic <div> html elements into the
generated document. This is useful for styling and other similar reasons.

Any arguments given to the directive will be added as classes to the resulting
element.

This extension is originally from
https://github.com/dnnsoftware/Docs/blob/master/common/ext/div.py
and is licensed under the MIT license (see source file comments for the
license text).

Usage example:

.. div:: css-class-1 css-class-2

  Element contents (_parsed_ as **RST**). Note the blank line and the
  indentation.
'''
import sys
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives


# https://github.com/dnnsoftware/Docs/blob/master/common/ext/div.py

# The MIT License (MIT)

# Copyright (c) 2015 DNN Software

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class DivNode(nodes.General, nodes.Element):

    def __init__(self, text):
        super(DivNode, self).__init__()

    @staticmethod
    def visit_div(self, node):
        self.body.append(self.starttag(node, 'div'))

    @staticmethod
    def depart_div(self, node=None):
        self.body.append('</div>\n')

class DivDirective(Directive):

    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {'name': directives.unchanged}
    has_content = True

    def run(self):
        self.assert_has_content()
        text = '\n'.join(self.content)
        try:
            if self.arguments:
                classes = directives.class_option(self.arguments[0])
            else:
                classes = []
        except ValueError:
            raise self.error(
                'Invalid class attribute value for "%s" directive: "%s".'
                % (self.name, self.arguments[0]))
        node = DivNode(text)
        node['classes'].extend(classes)
        self.add_name(node)
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]
