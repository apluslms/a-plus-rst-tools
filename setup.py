'''
This extension setup bundes the different a-plus custom directives.

The bundling was motivated by the shared node types and other shared modules.
Having unused directives will not have a significant performance impact.
If necessary, edit this setup to change the loaded directives.
'''
import yaml_writer
import aplus_nodes
from questionnaire2 import Questionnaire, SingleChoice


def prepare_env(app):
    app.env.aplus = {}
    app.env.aplus['exercises'] = {}


def setup(app):

    # Ensure the output directory for generated mooc-grader configuration.
    app.connect('builder-inited', yaml_writer.create_directory)
    app.connect('builder-inited', prepare_env)

    # Add node type that can describe HTML elements and store configurations.
    app.add_node(
        aplus_nodes.html,
        html=(aplus_nodes.visit_html, aplus_nodes.depart_html)
    )

    # Load the questionnaire directives.
    app.add_directive('questionnaire', Questionnaire)
    app.add_directive('pick-one', SingleChoice)
    #app.add_directive('pick-any',  MultipleChoice)
    #app.add_directive('freetext',  FreeText)
    #app.add_directive('agree-group',  AgreeGroup)
    #app.add_directive('agree-item',  AgreeItem)
