"""
Directive for creating nested multirow columns with Bootstrap.

Designed to be used with the point-of-interest directive.

Options
:width: sets column width. Maximum value 12.
:column-class: Bootstrap classes can be applied. See example below.

More about the Bootstrap classes https://getbootstrap.com/docs/3.4/css/#helper-classes-backgrounds


.. point-of-interest:: Test

   .. row::

     .. column::
       :width: 8
       :column-class: bg-warning text-center

       .col-8 this is column's content.

       .. row::

         .. column::
           :width: 6
           :column-class: bg-light

           .col-6

         .. column::
           :width: 6
           :column-class: bg-secondary

           .col-6

     .. column::
       :width: 4
       :column-class: bg-success

       .col-4

"""

from docutils.parsers.rst import Directive, directives
from docutils import nodes

import aplus_nodes


class ColumnNode(nodes.General, nodes.Element):

    def __init__(self):
        super(ColumnNode, self).__init__()

    @staticmethod
    def visit_column(self, node):
        self.body.append(self.starttag(node, 'div'))

    @staticmethod
    def depart_column(self, node=None):
        self.body.append('</div>\n')


class Column(Directive):
    option_spec = {
        'width': directives.unchanged,
        'column-class': directives.unchanged,
    }

    has_content = True

    def run(self):
        self.assert_has_content()
        node = ColumnNode()
        if 'width' in self.options:
            # Bootstrap 3 does not support automatic widths in columns.
            col_width = str(self.options['width']).strip()
            if not col_width:
                col_width = ""
            else:
                col_width = "-" + col_width
        else:
            col_width = ""
        node['classes'].append('col-sm' + col_width)

        if 'column-class' in self.options:
            column_classes = [c.strip() for c in str(self.options['column-class']).split()]
            column_classes = [c for c in column_classes if c]
            if column_classes:
                node['classes'].extend(column_classes)

        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class Row(Directive):

    has_content = True

    def run(self):
        self.assert_has_content()
        container_class = 'row'
        row_container_opts = {
            'class': container_class,
        }

        row_container = aplus_nodes.html('div', row_container_opts)
        self.state.nested_parse(self.content, self.content_offset, row_container)

        return [row_container]


def setup(app):
    ignore_visitors = (aplus_nodes.visit_ignore, aplus_nodes.depart_ignore)
    app.add_directive('row', Row)

    app.add_node(ColumnNode, html=(ColumnNode.visit_column, ColumnNode.depart_column),
                 latex=ignore_visitors)
    app.add_directive('column', Column)
