# -*- coding: utf-8 -*-
import docutils
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from html import escape
from collections import Counter
import re
import os
from sphinx.directives.code import CodeBlock
from sphinx.errors import SphinxError
from sphinx.util.fileutil import copy_asset
from sphinx.util import logging
from operator import itemgetter

import aplus_nodes

CSS_FILE = 'css/annotated.css'
JS_FILE = 'js/annotated.js'

assets_path = 'static'

logger = logging.getLogger(__name__)

annotated_section_counts = Counter()

class AnnotationError(SphinxError):
    category = 'Annotation error'


def clean_path(path):
  return re.sub(r"[/\\ :]+", "", path).replace(".rst", "")

def new_annotated_section_id(source_file_path):
  idprefix = clean_path(source_file_path).replace(clean_path(os.getcwd()), "")
  global annotated_section_counts
  annotated_section_counts[idprefix] += 1
  return "%s_%s" % (idprefix, str(annotated_section_counts[idprefix]))

def slicer(stringList):
  for i in range(0, len(stringList)):
    yield stringList[i:i+1]

class annotated_node(nodes.General, nodes.Element): pass

inline_anno_pattern = r"\[\[\[([^¶]+?)(?:¶(.*?))?\]\]\]"   # [[[annotation]]] or [[[annotation¶replacement]]]

class AnnotatedSection(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec = { }

    def run(self):
        self.assert_has_content()

        env = self.state.document.settings.env
        env.annotated_name = new_annotated_section_id(self.state_machine.get_source_and_line(self.lineno)[0])
        env.annotated_annotation_count = 0
        env.annotated_now_within = True

        node = annotated_node()

        for slice in slicer(self.content):
            if '.. code-block' in slice[0]:
                slice[0] = slice[0].replace('.. code-block', '.. altered-code-block')

        highest_annotation = self.assert_sanity(self.block_text)
        if not highest_annotation:
            return [self.state.document.reporter.error('Invalid annotation markers embedded in ' + self.block_text)]

        # Inline annotations numbered first (before nested_parse deals with annotation directives)
        inline_anno_count = len(re.findall(inline_anno_pattern, self.block_text))
        env.annotated_annotation_count += inline_anno_count

        self.state.nested_parse(self.content, 0, node)
        node['name'] = env.annotated_name
        if env.annotated_annotation_count != highest_annotation:
            return [self.state.document.reporter.error('Mismatching number of annotation captions (n=%s) and the embedded annotation markers (n=%s) in %s' % (env.annotated_annotation_count, highest_annotation, self.block_text))]

        env.annotated_now_within = False

        return [node]

    def assert_sanity(self, content):
        annotation_numbers_present = set(map(lambda matching: int(matching[0]), re.findall("\d«", content)))
        highest_present = max(annotation_numbers_present)
        all_until_highest = set(range(1, highest_present + 1))
        if annotation_numbers_present != all_until_highest:
          return None
        else:
          return highest_present


def visit_annotated_node(self, node):
    self.body.append('<div class="annotated ex-%s">\n' % (node['name']))
    env = self.builder.env
    env.redirect = self.body # store original output
    self.body = []           # create an empty one to receive the contents of the feedback line

def depart_annotated_node(self, node):
    env = self.builder.env
    parsed_html = self.body  # extract generated feedback line
    self.body = env.redirect # restore original output

    postprocessed_html = postprocess_annotation_tags(''.join(parsed_html), node['name'])
    postprocessed_html = postprocess_inline_annotations(postprocessed_html, node['name'])
    self.body.append(postprocessed_html)

    self.body.append("</div>\n")

def postprocess_inline_annotations(html, annotated_section_id):
    inline_anno_count = 0

    def make_annotation_span(match):
        nonlocal inline_anno_count
        inline_anno_count += 1
        annotation_text = match.group(1)
        bit_to_insert = match.group(2)
        replacement_attrib = ' data-replacement="' + bit_to_insert + '"' if bit_to_insert else ""
        html_bits = (annotated_section_id, inline_anno_count, replacement_attrib, annotation_text)
        return '<span class="codecomment comment-%s-%s"%s>%s</span>' % html_bits

    return re.sub(inline_anno_pattern, make_annotation_span, html)

def postprocess_annotation_tags(html, annotation_id):
    processed   = []
    openstack   = []
    selfclosing = []

    for part in re.split('(\d«» |\d«|»|\n)', html):
        if '«» ' in part:
            if (len(part) != 4) or (not part[0].isdigit()) or (part[3] != ' '):
                raise AnnotationError("Encountered illegal self-closing annotation tag in %s." % (annotation_id))
            processed.append('<span class="ex-%s loc%s">' % (annotation_id, part[0]))
            openstack.append(part[0])
            selfclosing.append(part[0])
        elif '«' in part:
            if (len(part) != 2) or (not part[0].isdigit()):
                raise AnnotationError("Encountered illegal annotation open tag in %s." % (annotation_id))
            processed.append('<span class="ex-%s loc%s">' % (annotation_id, part[0]))
            openstack.append(part[0])
        elif part == '»':
            if len(openstack) == 0:
                raise AnnotationError("Unbalanced annotation markers in %s." % (annotation_id))
            openstack.pop()
            processed.append('</span>')
        elif part == '\n':
            for tag in selfclosing:
                if len(openstack) == 0:
                    raise AnnotationError("Unbalanced annotation markers in %s." % (annotation_id))
                openstack.pop()
                processed.append('</span>')
            selfclosing = []
            processed.append(part)
        else:
            if  ('«' in part) or ('»' in part):
                raise AnnotationError("Encountered illegal annotation tag in %s." % (annotation_id))

            processed.append(part)

    if len(openstack) != 0:
        raise AnnotationError("Unbalanced annotation markers in %s." % (annotation_id)) ##

    return ''.join(processed)

class annotation_node(nodes.General, nodes.Element): pass

class Annotation(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = { }

    def run(self):
        self.assert_has_content()

        env = self.state.document.settings.env

        if not env.annotated_now_within:
          return [self.state.document.reporter.error('Not within an "annotated" directive:' + self.block_text.replace('\n', ' '))]

        node = annotation_node()
        self.state.nested_parse(self.content, 0, node)
        env.annotated_annotation_count += 1
        node['annotation-number'] = env.annotated_annotation_count
        node['name-of-annotated-section'] = env.annotated_name
        if self.arguments:
            node['replacement'] = self.arguments[0]
        return [node]

def visit_annotation_node(self, node):
    if 'replacement' in node:
        replacement_attrib = ' data-replacement="' + escape(node['replacement']) + '"'
    else:
        replacement_attrib = ""
    html_bits = (node['name-of-annotated-section'], node['annotation-number'], replacement_attrib)
    self.body.append('<div class="container codecomment comment-%s-%s"%s>' % html_bits)

def depart_annotation_node(self, node):
    self.body.append("</div>\n")


class altered_node(nodes.General, nodes.Element): pass

class AlteredCodeBlock(CodeBlock):
    def run(self):
        openstack   = []
        selfclosing = []
        annotations = []

        line_num = 0
        loc  = 0

        for line in slicer(self.content):
            processed   = []

            for part in re.split('(\d«» |\d«|»)', line[0]):
                if '«» ' in part:
                    openstack.append((part[0], line_num, loc))
                    selfclosing.append(part[0])
                elif '«' in part:
                    openstack.append((part[0], line_num, loc))
                elif '»' in part:
                    start = openstack.pop()
                    annotations.append((start[0], start[1], start[2], line_num, loc))
                else:
                    processed.append(part)
                    loc += len(part)

            for tag in selfclosing:
                start = openstack.pop()
                annotations.append((start[0], start[1], start[2], line_num, loc))

            selfclosing = []
            line_num += 1
            loc = 0

            line[0] = ''.join(processed)

        # run the original code-block on the now cleaned content
        originals = CodeBlock.run(self)

        # place the results as children of a node holding annotation info
        node = altered_node()
        node['annotations'] = annotations

        for item in originals:
            node.append(item)

        return [node]

def visit_altered_node(self, node):
    env = self.builder.env
    env.inner_redirect = self.body # store original output
    self.body = []           # create an empty one to receive the contents of the feedback line

def depart_altered_node(self, node):
    env = self.builder.env
    parsed_html = self.body  # extract generated feedback line
    self.body = env.inner_redirect # restore original output

    self.body.append(annotate(''.join(parsed_html), node.parent['name'], node['annotations']))

def create_open_tag(number, section_name):
    return '<span class="ex-%s loc%s">' % (section_name, number)

def create_close_tag(number, section_name):
    return '</span>'

def turn_to_close_tag(tag):
    return '</%s>' % re.findall('<(\w+).*?>', tag)[0]

def annotate(html, section_name, annotations):
    # sorting the annotations by their ending points correctly orders the starting points
    # for two annotations starting in the same location are correctly nested
    annotations = sorted(annotations, key = lambda x:x[3:5], reverse=True)

    from collections import defaultdict
    startpoint_map = defaultdict(list)
    endpoint_map   = defaultdict(list)

    # collect split points
    for a in annotations:
        number= a[0]
        start = a[1:3]
        end   = a[3:5]
        startpoint_map[start].append(number)
        endpoint_map[end].append(number)


    html = html.replace("<span></span>", "") # temporary workaround for extra span created by Sphinx in Python 3
    parts = re.split('(<pre.*?>|</pre>)', html)

    # separate tags from text
    original = re.split('(<.*?>|\n)', parts[2])

    #add splits
    line = 0
    loc  = 0
    result = []
    last_open  = ''

    for item in original:
        if '</' in item:
            # closing tag

            result.append(item)
            last_open = ''

            # add any closing tags
            for number in endpoint_map[(line, loc)]:
                result.append(create_close_tag(number, section_name))

        elif '<' in item:
            # opening tag

            # add tags for opening annotations
            for number in startpoint_map[(line, loc)]:
                result.append(create_open_tag(number, section_name))

            last_open = item
            result.append(item)
        elif '\n' in item:
            # line change

            line += 1
            loc   = 0

            result.append(item)
        elif item:

            chars = re.findall('(&#?\w+;?|.)', item)

            # text element
            start_loc = loc
            end_loc   = loc + len(chars)

            # add tags for opening annotations
            if (not last_open):
                for number in startpoint_map[(line, loc)]:
                    result.append(create_open_tag(number, section_name))

            # iterate over possible split locations and append chars

            for char in chars:
                if (loc != start_loc) & (loc != end_loc) & (((line, loc) in endpoint_map) | ((line, loc) in startpoint_map)):
                    # somewhere in the middle
                    if last_open:
                        result.append(turn_to_close_tag(last_open))
                    for number in endpoint_map[(line, loc)]:
                       result.append(create_close_tag(number, section_name))
                    for number in startpoint_map[(line, loc)]:
                       result.append(create_open_tag(number, section_name))
                    if last_open:
                        result.append(last_open)

                result.append(char)
                loc += 1

            # add tags for closing annotations
            if (not last_open):
                for number in endpoint_map[(line, loc)]:
                    result.append(create_close_tag(number, section_name))

    content = ''.join(result)
    return ''.join([parts[0], parts[1], content, parts[3], parts[4]])

def add_assets(app):
    # This method reads the `include_annotated_css` and `include_annotated_js`
    # settings from the conf.py file located in the course directory. If such
    # settings are not found, the default settings defined in the setup()
    #  method will be used instead
    attrs = {"data-aplus": "yes"}
    app.config.include_annotated_css and app.add_css_file(CSS_FILE, **attrs)
    app.config.include_annotated_js and app.add_js_file(JS_FILE, **attrs)

def copy_asset_files(app, exc):

    if exc:
        return
        
    # The files are added to the _build/html/_static/css folder. 
    if app.config.include_annotated_css:
        logger.info('Copying CSS files from the annotated directive to the _static folder... ')
        html_static_path_css = os.path.join(assets_path, CSS_FILE)
        local_path_css = os.path.join(os.path.dirname(__file__), html_static_path_css)
        copy_asset(local_path_css, os.path.join(app.outdir, '_static', 'css'))
        logger.info('done')
    
    # The files are added to the _build/html/_static/js folder. 
    if app.config.include_annotated_js:
        logger.info('Copying JS files from the annotated directive to the _static folder... ')
        html_static_path_js = os.path.join(assets_path, JS_FILE)
        local_path_js = os.path.join(os.path.dirname(__file__), html_static_path_js)
        copy_asset(local_path_js, os.path.join(app.outdir, '_static', 'js'))
        logger.info('done')
        
def setup(app):

    ignore_visitors = (aplus_nodes.visit_ignore, aplus_nodes.depart_ignore)

    app.add_config_value('include_annotated_css', False, 'html')
    app.add_config_value('include_annotated_js', False, 'html')

    app.add_node(annotated_node, html=(visit_annotated_node, depart_annotated_node),
            latex=ignore_visitors)
    app.add_directive('annotated', AnnotatedSection)

    app.add_node(annotation_node, html=(visit_annotation_node, depart_annotation_node),
            latex=ignore_visitors)
    app.add_directive('annotation', Annotation)

    app.add_node(altered_node, html=(visit_altered_node, depart_altered_node),
            latex=ignore_visitors)
    app.add_directive('altered-code-block', AlteredCodeBlock)

    app.connect('builder-inited', add_assets)

    app.connect('build-finished', copy_asset_files)
