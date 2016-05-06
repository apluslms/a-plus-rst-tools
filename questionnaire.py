# -*- coding: utf-8 -*-
"""
    Generates multiple-choice questionnaires from ReST directives.

    .. questionnaire:: 13 A10

       Questionnaires can contain ReST just like any normal directives.
       The two parameters tell the number of the questionnaire and the
       points awarded for the whole questionnaire.

       .. freetext:: 1 siw
          :own-line:
          :length: 10

          This text _is_ the question in a free text question.
          The first parameter defines the points awarded for this particular
          item in the questionnaire and the second optional parameter defines
          how to match the contents. The match types are described in detail
          later in the file. There are three possible options:
          * length: the width of the input field/area (default 50)
          * height: the height of the input field/area (default 1)
          * own-line: whether the input field should be laid out on a
              separate line (only done if height is 1)

          kissa  § This is the feedback shown to a user that submitted the correct response "kissa". The feedback is optional.
          !nakki § This is shown to anyone who did not answer "nakki". This line is optional.
          pöllö  § This additional feedback for a particular incorrect answer is also optional.

       Normal ReST blocks can be interleaved with the questions.

       .. pick-one:: 1

           Once again question text that can contain *ReST*.

           And multiple paragraphs.

           *a. This is the choice text for the correct answer (marked with an asterisk).
           b. This is another choice
           c. and one more

           a § That's right, great! This feedback paragraph has to contain at least one feedback item with a §, unless you are clever.
           b § No, that's not correct.

        .. pick-any:: 2

           One question more --- a multiple choice question.

           *a. This one's correct.
           *b. And so is this one.

           !a § That was so simple, how did you get that wrong!!!

"""
import docutils
import os

import codecs
from os import path
from docutils import nodes
from docutils.parsers.rst import directives

from sphinx.locale import _
from sphinx.util.compat import Directive
from sphinx.util.osutil import ensuredir
from sphinx.util.nodes import nested_parse_with_titles

# TODO: refactor the directive classes so that the division bw chapter feedback
#       questionnaires and exercise questionnaires is not so messed up


# ********************* NODES ***********************************

class multi_node(nodes.General,  nodes.Element): pass

class radio_node(nodes.General,  nodes.Element): pass

class freetext_node(nodes.General,  nodes.Element): pass

class choice_node(nodes.General, nodes.Element): pass

class questionnaire_node(nodes.General, nodes.Element): pass

class feedback_node(nodes.General, nodes.Element): pass

def slicer(stringList):
  for i in range(0, len(stringList)):
    yield stringList[i:i+1]



# ******************* PARSING PHASE : DIRECTIVES *********************

class ChoiceQuestion(Directive):
    """
    A single choice question entry for automatic goblin inclusion
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = { "class" : directives.class_option }


    def create_choice_node(self, isFeedback):
        raise NotImplementedError("Subclasses should implement this")

    def create_node(self, isFeedback):
        raise NotImplementedError("Subclasses should implement this")

    def run(self):
        env = self.state.document.settings.env

        env.questionnaire_question_count += 1

        node   = self.create_node(env.questionnaire_is_feedback)
        node['number']    = env.questionnaire_question_count
        node['correct']   = []
        node['feedbacks'] = []
        node['classes'] += self.options.get('class', [])

        self.assert_has_content()

        stops = list(loc for loc, val in enumerate(self.content) if val == u"")

        if node['is-feedback']:
            if len(stops) < 1:
                return [self.state.document.reporter.error('Wrong number of paragraphs in config of this question:\n' + self.block_text)]
            qcontent  = self.content[:stops[-1]]
            choices   = self.content[stops[-1]+1:]
        else:
            if len(stops) < 2:
                return [self.state.document.reporter.error('Too few paragraphs in config of this question:\n' + self.block_text)]
            qcontent  = self.content[:stops[-2]]
            choices   = self.content[stops[-2]+1:stops[-1]]
            feedbacks = self.content[stops[-1]+1:]


        # questions can contain ReST and must be parsed
        question = docutils.nodes.container()
        nested_parse_with_titles(self.state, qcontent, question)
        node.append(question)

        correct_list = []

        for choice in slicer(choices):              # choices must be _sliced_ to pieces to keep it a StringList
            (id, text) = choice[0].split(' ',1)     # split "a. question" to "a." and "question"
            (id, text) = (id.strip(), text.strip())
            choice[0] = text                        # replace the text in the stringlist before parse

            choicenode = self.create_choice_node(node['is-feedback'])  # create an option node
            nodes = docutils.nodes.paragraph()      # create a paragraph to receive the parsed ReST
            self.state.nested_parse(choice, 0, nodes)

            choicenode.append(nodes)
            node.append(choicenode)

            if "*" in id:
                correct_list += id.strip()[1:-1]

        node['correct'] += [str(node['number']) + ":" + ",".join(correct_list)]

        if node['is-feedback']:
            return [node]

        if len(self.arguments) < 1:
            return [self.state.document.reporter.error('Missing points argument of this question:\n' + self.block_text)]
        node['points'] = self.arguments[0]

        for feedback in slicer(feedbacks):
            feedbackLine = feedback[0].strip()
            if feedbackLine == u"I hereby declare that no feedback is necessary.":
                feedbackLine = u"I hereby declare that no feedback is necessary.§Nice answer. This feedback should egg you on."
            elif not u"§" in feedbackLine:
                return [self.state.document.reporter.error('Missing or malformed feedback block in this question:\n' + self.block_text)]

            (id, text) = feedbackLine.split(u"§", 1)
            (id, text) = (id.strip(), text.strip())
            feedback[0] = text

            # wrap the feedback in a feedback node that gets special treatment in the visit functions
            fnode = feedback_node()
            fnode['number'] = str(node['number']) + ":" + id
            ftext = docutils.nodes.paragraph()
            self.state.nested_parse(feedback, 0, ftext)
            fnode.append(ftext)
            node.append(fnode)

        return [node]


class MultipleChoice(ChoiceQuestion):
    """
    A multiple choice question entry for automatic goblin inclusion
    """
    def create_node(self, isFeedback):
        node = multi_node()
        node['is-feedback'] = isFeedback
        return node

    def create_choice_node(self, isFeedback):
        node = choice_node()
        node['type'] = "checkbox"
        node['is-feedback'] = isFeedback
        return node

class SingleChoice(ChoiceQuestion):
    """
    A multiple choice question entry for automatic goblin inclusion
    """
    def create_node(self, isFeedback):
        node = radio_node()
        node['is-feedback'] = isFeedback
        return node

    def create_choice_node(self, isFeedback):
        node = choice_node()
        node['type'] = "radio"
        node['is-feedback'] = isFeedback
        return node


class Questionnaire(Directive):
    """
    A questionnaire entry for automatic goblin inclusion
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 2
    final_argument_whitespace = False
    option_spec = { 'chapter-feedback': directives.flag,
                    'weekly-feedback': directives.flag,
                    'course-feedback': directives.flag
                     }

    def run(self):
        env = self.state.document.settings.env
        env.questionnaire_question_count = 0
        env.questionnaire_is_feedback = 'chapter-feedback' in self.options or 'weekly-feedback' in self.options or 'course-feedback' in self.options

        node = questionnaire_node()
        node['chapter-feedback'] = 'chapter-feedback' in self.options
        node['weekly-feedback']  = 'weekly-feedback' in self.options
        node['course-feedback']  = 'course-feedback' in self.options

        if not env.questionnaire_is_feedback:
            if len(self.arguments) < 2:
                return [self.state.document.reporter.error('Missing arguments (id and/or points) in questionnaire:\n' + self.block_text)]
            node['exercise_number'] = self.arguments[0]
            node['points']          = self.arguments[1]

            (source, line) = self.state.state_machine.get_source_and_line()
            # ugly way to get a relative path
            path_snippet = str(source)[len(env.srcdir) + 2:]
            node['k00_chapter_num'] = int(path_snippet[0:2])

        self.assert_has_content()

        # questionnaires contain questions and must be parsed
        question = docutils.nodes.paragraph()
        nested_parse_with_titles(self.state, self.content, question)
        node.append(question)

        return [node]




class FreeText(Directive):
    """
    A free text question entry for automatic goblin inclusion
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 2
    final_argument_whitespace = False
    option_spec = {'length': directives.positive_int,
                   'height': directives.positive_int,
                   'own-line': directives.flag,
                   'main-feedback': directives.flag,
                   'required': directives.flag,
                   'no-standard-prompt': directives.flag,
                   'shorter-prompt': directives.flag,
                    "class" : directives.class_option,
                  }

    def run(self):

        env = self.state.document.settings.env

        env.questionnaire_question_count += 1

        node   = freetext_node()
        node['number']    = env.questionnaire_question_count
        node['correct']   = ""

        node['feedbacks'] = []
        node['length']   = self.options.get('length', 50)
        node['height']   = self.options.get('height', 1)
        node['own-line'] = node['height'] > 1 or 'own-line' in self.options
        node['main-feedback'] = 'main-feedback' in self.options
        node['is-feedback'] = env.questionnaire_is_feedback
        node['classes'] += self.options.get('class', [])

        node['required'] = 'required' in self.options
        node['no-standard-prompt'] = 'no-standard-prompt' in self.options
        node['shorter-prompt'] = 'shorter-prompt' in self.options

        if node['is-feedback']:
            qcontent      = self.content
        else:
            stops = list(loc for loc, val in enumerate(self.content) if val == u"")
            if len(stops) == 0:
                return [self.state.document.reporter.error('Too few paragraphs in config of this question:\n' + self.block_text)]
            qcontent      = self.content[:stops[-1]]
            finalBlock    = self.content[stops[-1]+1:]

        # questions can contain ReST and must be parsed
        question = docutils.nodes.container()
        nested_parse_with_titles(self.state, qcontent, question)
        node.append(question)

        if node['is-feedback']:
            return [node]

        if len(self.arguments) < 2:
            return [self.state.document.reporter.error('Missing one or more argument of this question (expected points and assessment):\n' + self.block_text)]
        node['points'] = self.arguments[0]
        node['modifiers'] = self.arguments[1]

        ''' second argument controls matching in goblin (OUTDATED)

            d    floating point, 0.02 tolerance
            c    multiple choice (automatically on)
            s    non-case-sensitive string matching (automatically on)
            siw  string, ignore whitespace, ignore case
            i    integer
            ss   string case-sensitive
            r    regexp
            riw  regexp, ignore user's whitespace
            l    list of characters, free ordering
        '''

        correctLine = finalBlock.data[0]
        if u"§" in correctLine:
            correctAnswer = correctLine.split(u"§", 1)[0].strip()
        else:
            correctAnswer = correctLine.strip()
        node['correct'] = [str(node['number']) + ":" + correctAnswer]

        feedbackPresent = u"§" in correctLine or len(finalBlock) > 1
        atFirst = True
        if feedbackPresent:
            for feedback in slicer(finalBlock):
                if not u"§" in feedback[0]:
                    if atFirst:
                        atFirst = False
                        continue
                    else:
                        return [self.state.document.reporter.error('Missing or malformed feedback block in Question:\n' + self.block_text)]

                (id, text) = feedback[0].split(u"§", 1)
                (id, text) = (id.strip(), text.strip())
                feedback[0] = text

                # wrap the feedback in a feedback node that gets special treatment in the visit functions
                fnode = feedback_node()
                fnode['number'] = str(node['number']) + ":" + id
                ftext = docutils.nodes.paragraph()
                self.state.nested_parse(feedback, 0, ftext)
                fnode.append(ftext)
                node.append(fnode)
                atFirst = False

        return [node]


# **************** WRITING PHASE FUNCTIONS *****************

def visit_questionnaire_node(self, node):
    if node['chapter-feedback']:
        self.body.append('<div id="chapter-feedback"><form>')
        return

    if node['weekly-feedback']:
        self.body.append('<div id="weekly-feedback"><form>')
        return

    if node['course-feedback']:
        self.body.append('<div id="course-feedback-questionnaire"><form>')
        return

    self.body.append('<div class="multiple-choice" data-id="%s" points="%s"><form>\n' % (node['exercise_number'],node['points']))
    env = self.builder.env

    # init the questionnaire lists. these get filled in by the child node visit functions.
    env.questionnaire_correct_list  = []
    env.questionnaire_point_list    = []
    env.questionnaire_feedback_list = []
    env.questionnaire_modifier_list = []

def depart_questionnaire_node(self, node):
    """ departing a questionnaire node outputs both the closing tag of the form and
        writes out the questionnaire file and model answer needed by goblin.
    """
    self.body.append("\n</form></div>")

    if node['chapter-feedback'] or node['weekly-feedback'] or node['course-feedback']:
        return

    env = self.builder.env

    exercise_code = "%d%02d1" % (node['k00_chapter_num'], int(node['exercise_number']))
    exercise_dir = path.join(env.questionnaire_dir, exercise_code)
    if not os.path.exists(exercise_dir):
        os.makedirs(exercise_dir)

    questionnaire_file = path.join(exercise_dir, "%s.xml" % (exercise_code))
    #f = codecs.open(questionnaire_file, 'w', self.builder.config.html_output_encoding)
    f = codecs.open(questionnaire_file, "w", "utf-8")
    f.write(u"\n".join(env.questionnaire_correct_list))
    f.write(u"\n\n")
    f.write(u"\n".join(env.questionnaire_point_list))
    f.write(u"\n\n")
    f.write(u"\n".join(env.questionnaire_feedback_list))

    if env.questionnaire_modifier_list:
        f.write(u"\n\n")
        f.write(u"\n".join(env.questionnaire_modifier_list))

    f.close()

    model_dir = path.join(exercise_dir, "model")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model_file = path.join(model_dir, "choice.txt")
    f = codecs.open(model_file, "w", "utf-8")
    f.write(u"\n".join(env.questionnaire_correct_list))
    f.close()

def visit_radio_node(self, node):
    self.body.append('\n<div class="multiple-choice-question %s">\n' % " ".join(node['classes']))
    if node['is-feedback']:
        return
    env = self.builder.env
    env.questionnaire_correct_list += node['correct']
    env.questionnaire_point_list   += [str(node['number']) + ":" + str(node['points'])]

def depart_radio_node(self, node):
    self.body.append("</div>")

def visit_multi_node(self, node):
    self.body.append('\n<div class="multiple-choice-question %s">\n' % " ".join(node['classes']))
    if node['is-feedback']:
        return
    env = self.builder.env
    env.questionnaire_correct_list += node['correct']
    env.questionnaire_point_list   += [str(node['number']) + ":" + str(node['points'])]

def depart_multi_node(self, node):
    self.body.append("</div>")

def visit_choice_node(self, node):
    self.body.append('<input type="' + node['type'] + '">')

def depart_choice_node(self, node):
    self.body.append("<br />\n")

def visit_freetext_node(self, node):
    if node['main-feedback']:
        classtext = "main-feedback-question"
        if node['required']:
            classtext += " required"
        else:
            classtext += " voluntary"
        if not node['no-standard-prompt']:
            classtext += " standard"
        if node['shorter-prompt']:
            classtext += " shorter"
    else:
        classtext = "multiple-choice-question"

    self.body.append('\n<div class="%s %s">\n' % (classtext, " ".join(node['classes'])))
    if node['is-feedback']:
        return
    env = self.builder.env
    env.questionnaire_correct_list += node['correct']
    env.questionnaire_point_list   += [str(node['number']) + ":" + str(node['points'])]
    if node['modifiers']:
        env.questionnaire_modifier_list += [str(node['number']) + ":" + node['modifiers']]

def depart_freetext_node(self, node):
    if node['own-line']:
        positioning = 'class="place-on-own-line"'
    else:
        positioning = 'class="place-inline"'
    if node['height'] == 1:
        self.body.append(('<input type="text" size="%d" ' + positioning + '>\n') % node['length'])
    else:
        self.body.append(('<textarea rows="%d" cols="%d" ' + positioning + '></textarea>\n') % (node['height'], node['length']))
    self.body.append('</div>')


# NOTE! feedback nodes are parsed by sphinx and corresponding html gets generated but
# it is NOT included in the body of the document.

def visit_feedback_node(self, node):
    env = self.builder.env
    env.redirect = self.body # store original output
    self.body = []           # create an empty one to receive the contents of the feedback line

def depart_feedback_node(self, node):
    env = self.builder.env
    parsed_html = self.body  # extract generated feedback line
    self.body = env.redirect # restore original output
    env.questionnaire_feedback_list += [node['number'] + u"§" + u"".join(parsed_html)]



## AGREE-DISAGREEP-GROUPS FOR FEEDBACK FORMS

class agree_group_node(nodes.General, nodes.Element): pass

class AgreeGroup(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec = { "class" : directives.class_option }

    def run(self):
        self.assert_has_content()
        node = agree_group_node()
        nested_parse_with_titles(self.state, self.content, node)
        node['classes'] += self.options.get('class', [])
        return [node]

def visit_agree_group_node(self, node):
    self.body.append('<div class="agree-disagree-group %s" >' % " ".join(node['classes']))

def depart_agree_group_node(self, node):
    self.body.append("</div>\n")


class agree_item_node(nodes.General, nodes.Element): pass

class AgreeItem(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = { "class" : directives.class_option }

    def run(self):
        node = agree_item_node()
        node['text'] = self.arguments[0]
        node['classes'] += self.options.get('class', [])
        return [node]

def visit_agree_item_node(self, node):
    self.body.append('    <div class="agree-disagree-item %s">%s' % (" ".join(node['classes']), node['text']))

def depart_agree_item_node(self, node):
    self.body.append("</div>\n")


# SETUP A.K.A. MAIN


def ensure_dirs(app):
    '''Makes sure that the build directory has a directory for questionnaire files'''
    app.env.questionnaire_dir = path.join(app.builder.outdir, '_questionnaires')
    ensuredir(app.env.questionnaire_dir)


def setup(app):
    #currently unused config value, the idea was to possibly make offline checking of MCQs with javascript
    app.add_config_value('questionnaire_create_offline_feedback', False, 'html')

    # functions for the writing phase
    app.add_node(multi_node,
                 html=(visit_multi_node, depart_multi_node))
    app.add_node(radio_node,
                 html=(visit_radio_node, depart_radio_node))
    app.add_node(questionnaire_node,
                 html=(visit_questionnaire_node, depart_questionnaire_node))
    app.add_node(choice_node,
                 html=(visit_choice_node, depart_choice_node))
    app.add_node(freetext_node,
                 html=(visit_freetext_node, depart_freetext_node))
    app.add_node(feedback_node,
                 html=(visit_feedback_node, depart_feedback_node))
    app.add_node(agree_group_node,
                 html=(visit_agree_group_node, depart_agree_group_node))
    app.add_node(agree_item_node,
                 html=(visit_agree_item_node, depart_agree_item_node))

    # registration of the directives
    app.add_directive('questionnaire', Questionnaire)
    app.add_directive('pick-one', SingleChoice)
    app.add_directive('pick-any',  MultipleChoice)
    app.add_directive('freetext',  FreeText)
    app.add_directive('agree-group',  AgreeGroup)
    app.add_directive('agree-item',  AgreeItem)

    # when builder is inited, we create the questionnaire dir if needed
    app.connect('builder-inited', ensure_dirs)
