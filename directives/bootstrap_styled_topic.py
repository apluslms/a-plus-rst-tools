# -*- coding: utf-8 -*-
'''
Directive that inserts "topic" elements that are more friendly to css styling
using the bootstrap framework. Usage:

.. styled-topic::
  :class: css-class-1 css-class-2

  Topic must include content. All content is **parsed** _normally_ as RST.

  Note the blank line between the directive and its content, and the
  indentation.

An optional :class: option can be used to insert other css classes to the
resulting <div> element.

This extension also registers a conf.py value of
'bootstrap_styled_topic_classes'. It can be used to set default classes that are
added to all styled-topic directives. The default value is "dl-horizontal topic"
where "dl-horizontal" is useful for inserting bootstrap styled <dl> elements
into the div.
'''
from .div import DivNode
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives

class StyledTopicDirective(Directive):

    optional_arguments = 0
    option_spec = {'class': directives.class_option}
    has_content = True

    def run(self):
        self.assert_has_content()
        env = self.state.document.settings.env
        text = '\n'.join(self.content)
        node = DivNode(text)

        node['classes'].extend(directives.class_option(env.config['bootstrap_styled_topic_classes']))
        if 'class' in self.options:
            node['classes'].extend(self.options['class'])

        self.state.nested_parse(self.content, self.content_offset, node)

        return [node]
