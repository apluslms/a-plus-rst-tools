# -*- coding: utf-8 -*-
import docutils
from docutils import nodes
from docutils.parsers.rst import Directive, directives

import aplus_nodes

# DIRECTIVE FOR ARTICULATE STORYLINE BLOCKS: story

class story_node(nodes.General, nodes.Element): pass

class BasicStory(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True             # allows spaces in name of story, i.e., the file name
    option_spec = { 'story-height': directives.positive_int, 'story-width': directives.positive_int }

    def run(self):
        node = story_node()
        node['name'] = self.arguments[0]
        if 'story-width' in self.options:
            node['story-width'] = self.options['story-width']
        else:
            node['story-width'] = 865
        if 'story-height' in self.options:
            node['story-height'] = self.options['story-height']
        else:
            node['story-height'] = 690
        return [node]

def visit_story_node(self, node):
    self.body.append('<iframe class="articulate-story" width="%s" height="%s" style="border: none" src="../_static/storylines/%s - Storyline output/story.html">' % (node['story-width'],node['story-height'],node['name']))

def depart_story_node(self, node):
    self.body.append("</iframe>\n")


# DIRECTIVE FOR JSVEE VISUALIZATIONS: jsvee

class jsvee_node(nodes.General, nodes.Element): pass

class JSVEE(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = { }

    def run(self):
        node = jsvee_node()
        node['id'] = self.arguments[0]
        return [node]

def visit_jsvee_node(self, node):
    self.body.append('<div class="jsvee-animation" data-id="%s">' % (node['id']))

def depart_jsvee_node(self, node):
    self.body.append("</div>\n")



# DIRECTIVE FOR YOUTUBE VIDEOS: youtube

class youtube_node(nodes.General, nodes.Element): pass

class YouTubeVideo(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = { 'video-height': directives.positive_int, 'video-width': directives.positive_int }

    def run(self):
        node = youtube_node()
        node['id'] = self.arguments[0]
        if 'video-width' in self.options:
            node['video-width'] = self.options['video-width']
        else:
            node['video-width'] = 640
        if 'video-height' in self.options:
            node['video-height'] = self.options['video-height']
        else:
            node['video-height'] = 400
        return [node]

def visit_youtube_node(self, node):
    self.body.append('<iframe class="youtube-video" width="%s" height="%s" src="https://www.youtube-nocookie.com/embed/%s?rel=0" frameborder="0" allowfullscreen>' % (node['video-width'],node['video-height'],node['id']))

def depart_youtube_node(self, node):
    self.body.append("</iframe>\n")


# DIRECTIVE FOR VIDEOS: local-video

class video_node(nodes.General, nodes.Element): pass

class LocalVideo(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True             # allows spaces in file name
    option_spec = { 'video-width': directives.positive_int }

    def run(self):
        node = video_node()
        node['id'] = self.arguments[0]
        if 'video-width' in self.options:
            node['video-width'] = self.options['video-width']
        else:
            node['video-width'] = 650
        return [node]

def visit_video_node(self, node):
    self.body += '<video class="local-video" width="%s" controls>' % node['video-width']
    self.body += '<source src="../_static/videot/%s.mp4"  type="video/mp4">'  % node['id']
    self.body += '<source src="../_static/videot/%s.webm" type="video/webm">' % node['id']
    self.body += 'Your browser does not support the HTML5 video tag. Please use a browser that does.'
    self.body += '</video>'

def depart_video_node(self, node):
    self.body.append("</video>\n")



# DIRECTIVE FOR INTERNAL FRAMES: embedded-page

class iframe_node(nodes.General, nodes.Element): pass

class IFrame(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True             # allows spaces in url
    option_spec = { 'frame-height': directives.positive_int, 'frame-width': directives.positive_int }

    def run(self):
        node = iframe_node()
        node['url'] = self.arguments[0]
        if 'frame-width' in self.options:
            node['frame-width'] = self.options['frame-width']
        else:
            node['frame-width'] = 850
        if 'frame-height' in self.options:
            node['frame-height'] = self.options['frame-height']
        else:
            node['frame-height'] = 500
        return [node]

def visit_iframe_node(self, node):
    self.body.append('<iframe class="embedded-page" width="%spx" height="%spx" src="%s">' % (node['frame-width'],node['frame-height'],node['url']))

def depart_iframe_node(self, node):
    self.body.append("</iframe>\n")

# SETUP AKA "MAIN"

def setup(app):

    ignore_visitors = (aplus_nodes.visit_ignore, aplus_nodes.depart_ignore)

    app.add_node(story_node, html=(visit_story_node, depart_story_node),
            latex=ignore_visitors)
    app.add_directive('story', BasicStory)

    app.add_node(jsvee_node, html=(visit_jsvee_node, depart_jsvee_node),
            latex=ignore_visitors)
    app.add_directive('jsvee', JSVEE)

    app.add_node(youtube_node, html=(visit_youtube_node, depart_youtube_node),
            latex=ignore_visitors)
    app.add_directive('youtube', YouTubeVideo)

    app.add_node(video_node, html=(visit_video_node, depart_video_node),
            latex=ignore_visitors)
    app.add_directive('local-video', LocalVideo)

    app.add_node(iframe_node, html=(visit_iframe_node, depart_iframe_node),
            latex=ignore_visitors)
    app.add_directive('embedded-page', IFrame)
