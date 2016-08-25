'''
This extension setup bundes the different a-plus custom directives.

The bundling was motivated by the shared node types and other shared modules.
Having unused directives will not have a significant performance impact.
If necessary, edit this setup to select the loaded directives.
'''
import toc_config
import aplus_nodes
from directives.meta import aplusmeta, AplusMeta
from directives.questionnaire import Questionnaire, SingleChoice, MultipleChoice, FreeText, AgreeGroup, AgreeItem
from directives.submit import SubmitForm

def setup(app):

    # Register new settings.
    app.add_config_value('course_title', None, 'html')
    app.add_config_value('course_open_date', None, 'html')
    app.add_config_value('course_close_date', None, 'html')
    app.add_config_value('questionnaire_default_submissions', 5, 'html')
    app.add_config_value('program_default_submissions', 10, 'html')
    app.add_config_value('default_min_group_size', 1, 'html')
    app.add_config_value('default_max_group_size', 1, 'html')
    app.add_config_value('use_wide_column', True, 'html')
    app.add_config_value('append_content', [], 'html')

    # Connect configuration generation to events.
    app.connect('builder-inited', toc_config.prepare)
    app.connect('build-finished', toc_config.write)

    # Add node type that can describe HTML elements and store configurations.
    app.add_node(
        aplus_nodes.html,
        html=(aplus_nodes.visit_html, aplus_nodes.depart_html)
    )

    # The directive for injecting document meta data.
    app.add_node(aplusmeta)
    app.add_directive('aplusmeta', AplusMeta)

    # The questionnaire directives.
    app.add_directive('questionnaire', Questionnaire)
    app.add_directive('pick-one', SingleChoice)
    app.add_directive('pick-any',  MultipleChoice)
    app.add_directive('freetext',  FreeText)
    app.add_directive('agree-group',  AgreeGroup)
    app.add_directive('agree-item',  AgreeItem)

    # The submit directive.
    app.add_directive('submit', SubmitForm)
