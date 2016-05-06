# -*- coding: utf-8 -*-
"""
   Tuottaa näistä:
   
     .. submit:: 123 A100
   
   näitä:
   
     <div class="submit-exercise" data-id="123" points="A100"></div>
     
   Ja näistä:
   
     .. rubyric:: jotain
     
   näitä:
   
     <div class="submit-rubyric-exercise" data-id="jotain"></div> 

   Ja siinäpä se.
"""
import docutils

from docutils import nodes

from sphinx.util.compat import Directive



# SUBMIT-PROGRAM

class submit_node(nodes.General,  nodes.Element): pass

class SubmitProgramForm(Directive):
    has_content = False
    required_arguments = 2
    optional_arguments = 0
    option_spec = {}

    def run(self):
        node = submit_node()
        node['exercise_number'] = self.arguments[0]
        node['points']          = self.arguments[1]
        return [node]

def visit_submit_node(self, node):
    self.body.append('<div class="submit-exercise" data-id="%s" points="%s">' % (node['exercise_number'],node['points']))
    
def depart_submit_node(self, node):
    self.body.append("</div>\n")


# RUBYRIC

class rubyric_node(nodes.General, nodes.Element): pass

class Rubyric(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {} 

    def run(self):
        node = rubyric_node()
        node['id'] = self.arguments[0]
        return [node]

def visit_rubyric_node(self, node):
    self.body.append('<div class="submit-rubyric-exercise" data-id="%s">' % node['id'])

def depart_rubyric_node(self, node):
    self.body.append("</div>\n")


# SETUP

def setup(app):
    
    app.add_node(submit_node, html=(visit_submit_node, depart_submit_node))
    app.add_directive('submit-program', SubmitProgramForm)
    
    app.add_node(rubyric_node, html=(visit_rubyric_node, depart_rubyric_node))
    app.add_directive('rubyric', Rubyric)
    
    