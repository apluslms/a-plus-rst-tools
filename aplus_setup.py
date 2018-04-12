'''
This extension setup bundes the different a-plus custom directives.

The bundling was motivated by the shared node types and other shared modules.
Having unused directives will not have a significant performance impact.
If necessary, edit this setup to select the loaded directives.
'''
import toc_config
import aplus_nodes
from directives.meta import AplusMeta
from directives.questionnaire import Questionnaire, SingleChoice, MultipleChoice, FreeText, AgreeGroup, AgreeItem, AgreeItemGenerate
from directives.submit import SubmitForm
from directives.ae_input import ActiveElementInput
from directives.ae_output import ActiveElementOutput
from directives.hiddenblock import HiddenBlock
from directives.codeblock_lineref import LineRefCodeBlock


def setup(app):

    # Register new settings.
    app.add_config_value('course_title', None, 'html')
    app.add_config_value('submit_title', "{config_title}", 'html')
    app.add_config_value('course_open_date', None, 'html')
    app.add_config_value('course_close_date', None, 'html')
    app.add_config_value('questionnaire_default_submissions', 5, 'html')
    app.add_config_value('program_default_submissions', 10, 'html')
    app.add_config_value('default_min_group_size', 1, 'html')
    app.add_config_value('default_max_group_size', 1, 'html')
    app.add_config_value('default_late_date', None, 'html')
    app.add_config_value('default_late_penalty', 0.0, 'html')
    app.add_config_value('use_wide_column', True, 'html')
    app.add_config_value('append_content', [], 'html')
    app.add_config_value('override', {}, 'html')
    app.add_config_value('category_names', {}, 'html')
    app.add_config_value('static_host', None, 'html')
    app.add_config_value('ae_default_submissions', 0, 'html')

    # Connect configuration generation to events.
    app.connect('builder-inited', toc_config.prepare)
    app.connect('build-finished', toc_config.write)

    # Add node type that can describe HTML elements and store configurations.
    app.add_node(
        aplus_nodes.html,
        html=(aplus_nodes.visit_html, aplus_nodes.depart_html),
        latex=(aplus_nodes.visit_ignore, aplus_nodes.depart_ignore),
        # TODO: This html node is used by the A+ exercise directives that embed exercises into chapters.
        # The Latex builder could insert some content about the exercise to show where it would
        # be embedded in the HTML page instead of completely ignoring the exercise directive.
        # There could be a configuration option to control whether the Latex builder should
        # ignore exercises or not.
        # Note: even though these latex visitor functions do nothing, the exercise directives
        # nonetheless output some text to the Latex/PDF output. The text is even often duplicated
        # multiple times. This is possibly caused by broken aplus_nodes classes that interfere
        # with the builder output even though only the visitor functions should do that.
    )

    # The directive for injecting document meta data.
    app.add_node(
        aplus_nodes.aplusmeta,
        html=(aplus_nodes.visit_ignore, aplus_nodes.depart_ignore),
        latex=(aplus_nodes.visit_ignore, aplus_nodes.depart_ignore),
    )
    app.add_directive('aplusmeta', AplusMeta)

    # The questionnaire directives.
    app.add_directive('questionnaire', Questionnaire)
    app.add_directive('pick-one', SingleChoice)
    app.add_directive('pick-any',  MultipleChoice)
    app.add_directive('freetext',  FreeText)
    app.add_directive('agree-group',  AgreeGroup)
    app.add_directive('agree-item',  AgreeItem)
    app.add_directive('agree-item-generate', AgreeItemGenerate)

    # The submit directive.
    app.add_directive('submit', SubmitForm)
    app.add_directive('ae-input', ActiveElementInput)    
    app.add_directive('ae-output', ActiveElementOutput)
    app.add_directive('hidden-block', HiddenBlock)

