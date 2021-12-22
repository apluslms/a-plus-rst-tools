"""
This file is adapted for A+ from the sphinx-thebe project.

Changes:
* The Binderhub URL can be set in conf.py (thebe_config variable).
  It used to be a hardcoded value, mybinder.org.
* The JavaScript and CSS files are only copied to the build output directory
  if this Sphinx extension is enabled in conf.py.

Original source:
https://github.com/executablebooks/sphinx-thebe
https://github.com/executablebooks/sphinx-thebe/blob/v0.0.8/sphinx_thebe/__init__.py


MIT License

Copyright (c) 2018 Chris Holdgraf

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""A sphinx extension to enable interactive computations using thebe."""

import json
import os
from pathlib import Path

from docutils.parsers.rst import Directive, directives
from docutils import nodes
from sphinx.util import logging
from sphinx.util.fileutil import copy_asset

__version__ = "0.0.8"

CSS_FILE = 'css/thebe.css'
JS_FILE = 'js/thebe.js'

assets_path = 'static'

logger = logging.getLogger(__name__)

def st_static_path(app):
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "_static"))
    app.config.html_static_path.append(static_path)


def init_thebe_default_config(app, env, docnames):
    thebe_config = app.config.thebe_config
    defaults = {
        "selector": ".thebe",
        "selector_input": "pre",
        "selector_output": ".output",
    }
    for key, val in defaults.items():
        if key not in thebe_config:
            thebe_config[key] = val


def init_thebe_core(app, env):
    config_thebe = app.config["thebe_config"]
    if not config_thebe:
        logger.warning("Didn't find `thebe_config` in conf.py, add to use thebe")
        return

    # Add core libraries
    opts = {"async": "async", "data-aplus": "yes"}
    css_opts = {"data-aplus": "yes"}
    app.add_js_file(filename="https://unpkg.com/thebelab@latest/lib/index.js", **opts)
    app.add_js_file(filename="https://codemirror.net/mode/clike/clike.js", **opts)
    app.add_js_file(filename="https://codemirror.net/addon/hint/matchbrackets.js", **opts)
    app.add_css_file(filename="https://codemirror.net/theme/eclipse.css", **css_opts)
    app.add_css_file(filename="https://codemirror.net/theme/abcdef.css", **css_opts)


    # Add configuration variables
    thebe_config = f"""
        const thebe_selector = "{ app.config.thebe_config['selector'] }"
        const thebe_selector_input = "{ app.config.thebe_config['selector_input'] }"
        const thebe_selector_output = "{ app.config.thebe_config['selector_output'] }"
    """
    app.add_js_file(None, body=thebe_config, **opts)
    app.add_js_file(filename=JS_FILE, **opts)


def update_thebe_context(app, doctree, docname):
    """Add thebe config nodes to this doctree."""
    config_thebe = app.config["thebe_config"]
    if not config_thebe:
        return

    # Thebe configuration
    if config_thebe is True:
        config_thebe = {}
    if not isinstance(config_thebe, dict):
        raise ValueError(
            "thebe configuration must be `True` or a dictionary for configuration."
        )

    # Thebe configuration
    # Choose the kernel we'll use
    meta = app.env.metadata.get(docname, {})
    kernel_name = meta.get("thebe-kernel")
    if kernel_name is None:
        if meta.get("kernelspec"):
            kernel_name = json.loads(meta["kernelspec"]).get("name")
        else:
            kernel_name = "python3"

    # Codemirror syntax
    cm_language = kernel_name
    if "python" in cm_language:
        cm_language = "python"
    elif cm_language == "ir":
        cm_language = "r"
    elif "cpp" in cm_language:
        cm_language = "text/x-c++src"
    elif "c" in cm_language:
        cm_language = "text/x-csrc"
    else:
        cm_language = "python"

    # Get url for binderhub server
    binder_url = config_thebe.get(
        "binderUrl",
        "https://mybinder.org"
    )

    # Create the URL for the kernel request
    repo_url = config_thebe.get(
        "repository_url",
        "https://github.com/binder-examples/jupyter-stacks-datascience",
    )
    branch = config_thebe.get("repository_branch", "master")
    path_to_docs = config_thebe.get("path_to_docs", ".").strip("/") + "/"
    org, repo = _split_repo_url(repo_url)

    codemirror_theme = config_thebe.get("codemirror-theme", "eclipse")
    codemirror_indent_unit = 4
    codemirror_indent_with_tabs = "true"
    codemirror_electric_chars = "true"
    codemirror_line_numbers = "true"
    # NOTE: this assignment is not used in the thebe.js since the language is
    # later detected based on the kernel name.
    # Although overridden, this assignment might be useful later
    # when code-mirror mode is assigned with options in the configuration.
    codemirror_mode = cm_language

    codemirror_config = config_thebe.get("codemirror-config", None)
    if codemirror_config:
        codemirror_theme = codemirror_config.get("theme", codemirror_theme)
        codemirror_indent_unit = codemirror_config.get("indentUnit", codemirror_indent_unit)
        codemirror_indent_with_tabs = codemirror_config.get("indentWithTabs", codemirror_indent_with_tabs)
        codemirror_electric_chars = codemirror_config.get("electricChars", codemirror_electric_chars)
        codemirror_line_numbers = codemirror_config.get("lineNumbers", codemirror_line_numbers)
        codemirror_mode = codemirror_config.get("mode", codemirror_mode)
    # Update the doctree with some nodes for the thebe configuration
    thebe_html_config = f"""
    <script type="text/x-thebe-config">
    {{
        requestKernel: true,
        binderOptions: {{
            binderUrl: "{binder_url}",
            repo: "{org}/{repo}",
            ref: "{branch}",
        }},
        codeMirrorconfig: {{
            theme: '{codemirror_theme}',
            mode: '{codemirror_mode}',
            lineNumbers: {codemirror_line_numbers},
            electricChars: {codemirror_electric_chars},
            indentUnit: {codemirror_indent_unit},
            indentWithTabs: {codemirror_indent_with_tabs},
            matchBrackets: true
        }},
        kernelOptions: {{
            kernelName: "{kernel_name}",
            path: "{path_to_docs}{str(Path(docname).parent)}"
        }},
        predefinedOutput: true
    }}
    </script>
    """

    doctree.append(nodes.raw(text=thebe_html_config, format="html"))
    doctree.append(
        nodes.raw(text=f"<script>kernelName = '{kernel_name}'</script>", format="html")
    )


def _split_repo_url(url):
    """Split a repository URL into an org / repo combination."""
    if "github.com/" in url:
        end = url.split("github.com/")[-1]
        org, repo = end.split("/")[:2]
    elif "version.aalto.fi/" in url:
        end = url.split("github.com/")[-1]
        org, repo = end.split("/")[:2]
    else:
        logger.warning(f"Currently Thebe repositories must be on GitHub or Aalto gitlab, got {url}")
        org = repo = None
    return org, repo


class ThebeButtonNode(nodes.Element):
    """Appended to the doctree by the ThebeButton directive

    Renders as a button to enable thebe on the page.

    If no ThebeButton directive is found in the document but thebe
    is enabled, the node is added at the bottom of the document.
    """

    def __init__(self, rawsource="", *children, text="Run code", **attributes):
        super().__init__("", text=text)

    def html(self):
        text = self["text"]
        return (
            '<div class="thebe-button-container"><button title="{text}" class="thebelab-button thebe-launch-button"'
            'onclick="initThebe()">{text}</button></div>'.format(text=text)
        )


class ThebeButton(Directive):
    """Specify a button to activate thebe on the page

    Arguments
    ---------
    text : str (optional)
        If provided, the button text to display

    Content
    -------
    None
    """

    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False

    def run(self):
        kwargs = {"text": self.arguments[0]} if self.arguments else {}
        return [ThebeButtonNode(**kwargs)]


# Used to render an element node as HTML
def visit_element_html(self, node):
    self.body.append(node.html())
    raise nodes.SkipNode


# Used for nodes that do not need to be rendered
def skip(self, node):
    raise nodes.SkipNode


def setup(app):
    logger.verbose("Adding copy buttons to code blocks...")
    # Add our static path
    app.connect("builder-inited", st_static_path)

    # Set default values for the configuration
    app.connect("env-before-read-docs", init_thebe_default_config)

    # Include Thebe core docs
    app.connect("doctree-resolved", update_thebe_context)
    app.connect("env-updated", init_thebe_core)

    # configuration for this tool
    app.add_config_value("thebe_config", {}, "html")
    # override=True in case Jupyter Sphinx has already been loaded
    app.add_directive("thebe-button", ThebeButton, override=True)

    # Add relevant code to headers
    opts = {'data-aplus': 'yes'}
    app.add_css_file(CSS_FILE, **opts)

    # The files are added to the _build/html/_static/css folder.
    logger.info('Copying CSS files from the thebe-button directive to the _static folder... ')
    html_static_path_css = os.path.join(assets_path, CSS_FILE)
    local_path_css = os.path.join(os.path.dirname(__file__), html_static_path_css)
    copy_asset(local_path_css, os.path.join(app.outdir, '_static', 'css'))
    logger.info('done')

    # The files are added to the _build/html/_static/js folder.
    logger.info('Copying JS files from the thebe-button directive to the _static folder... ')
    html_static_path_js = os.path.join(assets_path, JS_FILE)
    local_path_js = os.path.join(os.path.dirname(__file__), html_static_path_js)
    copy_asset(local_path_js, os.path.join(app.outdir, '_static', 'js'))
    logger.info('done')

    # ThebeButtonNode is the button that activates thebe
    # and is only rendered for the HTML builder
    app.add_node(
        ThebeButtonNode,
        html=(visit_element_html, None),
        latex=(skip, None),
        textinfo=(skip, None),
        text=(skip, None),
        man=(skip, None),
        override=True,
    )

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
