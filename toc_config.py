import os
import re
import shlex

from docutils import nodes

from sphinx import addnodes
from sphinx.errors import SphinxError
from sphinx.util import logging

import aplus_nodes
import directives.meta
import lib.yaml_writer as yaml_writer
import lib.html_tools as html_tools
import lib.toc_languages as toc_languages
from lib.revealrule import parse_reveal_rule


logger = logging.getLogger(__name__)


def prepare(app):
    ''' Prepares environment for configuration values. '''
    yaml_writer.create_directory(app)


def set_config_language_for_doc(app, docname, source):
    '''Try to set config.language for the document (docname).

    The config.language value affects string localization in lib/translations.py
    and the Sphinx core.
    The language is read from the filename suffix (chapter_en.rst) or
    its parent directory (module01/en/chapter.rst). If the language can not
    be read from those sources, then config.language is not modified.
    '''
    if not app.config.enable_rst_file_language_detection:
        return

    filepath = app.env.doc2path(docname)
    folder = os.path.basename(os.path.dirname(filepath))

    # If language is not found in the docname or the folder, nothing is done.
    # Then app.env.config.language is defined in conf.py.
    if re.search(r"_[a-z]{2}$", docname):
        # docname has a postfix with the underscore, e.g., chapter_en.rst
        # docname does not include the file type extension .rst
        app.env.config.language = docname[-2:]
    elif re.fullmatch(r"^[a-z]{2}$", folder):
        # directory name is 2 characters long, e.g., "en"
        app.env.config.language = folder


def _is_multilingual_course(app):
    root = app.env.get_doctree(app.config.master_doc)
    tocs = list(root.traverse(addnodes.toctree))
    return tocs and tocs[0].get('rawcaption') == 'Select language'


def add_lang_suffix_to_links(app, docname, source):
    '''Add the language suffix to doc and ref link targets as well as ref link
    labels in multilingual courses.

    It is more convenient to write doc links without manually added language
    suffixes, e.g., :doc:`chapter1` instead of :doc:`chapter1_en`. This function
    adds the language suffixes automatically since Sphinx can not compile
    the link if the target file does not exist.

    Likewise, it is convenient to write identical ref link labels in the same
    place in all language versions of the chapter. Sphinx requires that labels
    are unique, thus language suffixes are automatically appended to the labels.
    The ref links in the RST chapters also refer to the labels without the
    language suffixes. The language suffixes are added automatically to
    the ref links.

    If the course uses a different format in links or for some other reason links
    need to stay untouched, set enable_doc_link_multilang_suffix_correction to
    False in order to disable doc link modifications and
    enable_ref_link_multilang_suffix_correction to False in order to disable
    ref link and label modifications. The variables are defined in conf.py.
    '''
    if (not app.config.enable_doc_link_multilang_suffix_correction and
            not app.config.enable_ref_link_multilang_suffix_correction):
        return

    lang_suffix = docname[-3:]
    # Check that the suffix is like _[a-z]{2}, for example, "_en".
    if not re.fullmatch(r"^_[a-z]{2}$", lang_suffix):
        return

    # The source argument is a list whose only element is the content of the source file.
    if app.config.enable_doc_link_multilang_suffix_correction:
        # Links of the form :doc:`link text <path/file>` (no language suffix _en in the file path)
        source[0] = re.sub(
            r":doc:`([^`<>]+)<([^`<>]+)(?<!_[a-z]{2})>`",
            r":doc:`\1<\2" + lang_suffix + r">`",
            source[0])
        # Links of the form :doc:`path/file` (no language suffix _en in the file path)
        source[0] = re.sub(
            r":doc:`([^`<>]+)(?<!_[a-z]{2})`",
            r":doc:`\1" + lang_suffix + r"`",
            source[0])

    if not app.config.enable_ref_link_multilang_suffix_correction:
        return

    # Add language suffixes to label definitions (if they haven't been added manually).
    # .. _mylabel:
    # Labels are defined on their own lines, but there may be whitespace before them (indentation).
    source[0] = re.sub(
        r"^(\s*)..\s+_([\w-]+)(?<!_[a-z]{2}):(\s*)$",
        r"\1.. _\2" + lang_suffix + r":\3",
        source[0],
        flags=re.MULTILINE)

    # Links of the form :ref:`link text <label-name>` (no language suffix _en in the label)
    source[0] = re.sub(
        r":ref:`([^`<>]+)<([^`<>]+)(?<!_[a-z]{2})>`",
        r":ref:`\1<\2" + lang_suffix + r">`",
        source[0])
    # Links of the form :ref:`label-name` (no language suffix _en in the label)
    source[0] = re.sub(
        r":ref:`([^`<>]+)(?<!_[a-z]{2})`",
        r":ref:`\1" + lang_suffix + r"`",
        source[0])


def write(app, exception):
    ''' Writes the table of contents level configuration. '''
    if app.builder.name != 'html':
        # course configuration YAML is only built with the Sphinx HTML builder
        # because some parts of the YAML generation have only been implemented
        # in the visit methods of the HTML builder (aplus_nodes functions
        # visit_html and depart_html)
        return
    if exception:
        return

    root = app.env.get_doctree(app.config.master_doc)

    # Check for language tree.
    keys = set()
    if _is_multilingual_course(app):
        logger.info('Detected language tree.')

        indexes = []
        for docname,_,doc in traverse_tocs(app, root):
            i = docname.rfind('_')
            if i < 0:
                raise SphinxError('Language postfix is required (e.g. docname_en): ' + docname)
            lang = docname[(i + 1):]
            logger.info('Traverse document elements to write configuration index ({}).'.format(lang))
            index = make_index(app, doc, language=lang)
            yaml_writer.write(yaml_writer.file_path(app.env, 'index_' + lang), index)
            indexes.append((lang, index))

        logger.info('Joining language tree to one index.')
        index = toc_languages.join(app, indexes)
        append_manual_content(app, index)
        yaml_writer.write(yaml_writer.file_path(app.env, 'index'), index)
        keys |= set(m['key'] for m in index['modules'])

    else:
        logger.info('Traverse document elements to write configuration index.')
        index = make_index(app, root)
        append_manual_content(app, index)
        yaml_writer.write(yaml_writer.file_path(app.env, 'index'), index)
        keys |= set(m['key'] for m in index['modules'])

    # Rewrite links for remote inclusion.
    keys |= {'toc', 'user', 'account'}
    html_tools.rewrite_outdir(app.outdir, keys, app.config.static_host)


def make_index(app, root, language=''):

    # metadata is defined in the field list of the RST document before any section
    # and other content. The master_doc is the main index.rst file of the course.
    # The syntax for field lists in RST is like this:
    # :course-start: 2019-09-16 12:00
    course_meta = app.env.metadata[app.config.master_doc]

    course_title = app.config.course_title
    course_open = course_meta.get('course-start', app.config.course_open_date)
    course_close = course_meta.get('course-end', app.config.course_close_date)
    # default late deadline for modules: if defined, all modules allow late submissions
    course_late = course_meta.get('course-default-late', app.config.default_late_date)
    course_penalty = course_meta.get('course-default-late-penalty', app.config.default_late_penalty)
    override = app.config.override

    course_reveal_submission_feedback = parse_reveal_rule(
        app.config.reveal_submission_feedback,
        'conf.py',
        None,
        'reveal_submission_feedback',
    )
    course_reveal_model_solutions = parse_reveal_rule(
        app.config.reveal_model_solutions,
        'conf.py',
        None,
        'reveal_model_solutions',
    )

    modules = []
    category_keys = []

    def get_static_dir(app):
        i = 0
        while i < len(app.outdir) and i < len(app.confdir) and app.outdir[i] == app.confdir[i]:
            i += 1
        outdir = app.outdir.replace("\\", "/")
        if outdir[i] == '/':
            i += 1
        return outdir[i:]

    def first_title(doc):
        titles = list(doc.traverse(nodes.title))
        return titles[0].astext() if titles else 'Unnamed'

    def first_meta(doc):
        metas = list(doc.traverse(directives.meta.aplusmeta))
        return metas[0].options if metas else {}

    # Tries to parse date from natural text.
    def parse_date(src, allow_empty=False):
        if allow_empty and not src:
            return None
        parts = src.split(' ', 1)
        d = parts[0]
        t = parts[1] if len(parts) > 1 else ''
        if re.match(r'^\d\d.\d\d.\d\d\d\d$', d):
            ds = d.split('.')
            d = ds[2] + '-' + ds[1] + '-' + ds[0]
        elif not re.match(r'^\d\d\d\d-\d\d-\d\d$', d):
            raise SphinxError('Invalid date ' + d)
        if not re.match(r'^\d\d(:\d\d(:\d\d)?)?$', t):
            t = '12:00'
        return d + ' ' + t

    def parse_float(src, default):
        return float(src) if src else default

    # Recursive chapter parsing.
    def parse_chapter(docname, doc, parent, module_meta):
        for config_file in [e.yaml_write for e in doc.traverse(aplus_nodes.html) if e.has_yaml('exercise')]:
            config = yaml_writer.read(config_file)
            if config.get('_external', False):
                exercise = config.copy()
                del exercise['_external']
            else:
                exercise = {
                    'key': config['key'],
                    'config': config['key'] + '.yaml',
                    'max_submissions': config.get('max_submissions', 0),
                    'max_points': config.get('max_points', 0),
                    'difficulty': config.get('difficulty', ''),
                    'points_to_pass': config.get('points_to_pass', 0),
                    'category': config['category'],
                    'min_group_size': config.get('min_group_size', 1),
                    'max_group_size': config.get('max_group_size', 1),
                    'confirm_the_level': config.get('confirm_the_level', False),
                }
            if 'configure' in config:
                exercise['configure'] = config['configure']
            allow_assistant_viewing = config.get('allow_assistant_viewing', app.config.allow_assistant_viewing)
            allow_assistant_grading = config.get('allow_assistant_grading', app.config.allow_assistant_grading)
            exercise.update({
                'status': config.get('status', 'unlisted'),
                'allow_assistant_viewing': allow_assistant_viewing,
                'allow_assistant_grading': allow_assistant_grading,
            })
            if 'scale_points' in config:
                exercise['max_points'] = config.pop('scale_points')

            # Reveal rules: try exercise config, then module meta, then course config.
            reveal_submission_feedback = config.get(
                'reveal_submission_feedback',
                module_meta.get(
                    'reveal-submission-feedback',
                    course_reveal_submission_feedback,
                )
            )
            if reveal_submission_feedback:
                exercise['reveal_submission_feedback'] = reveal_submission_feedback.copy()

            reveal_model_solutions = config.get(
                'reveal_model_solutions',
                module_meta.get(
                    'reveal-model-solutions',
                    course_reveal_model_solutions,
                )
            )
            if reveal_model_solutions:
                exercise['reveal_model_solutions'] = reveal_model_solutions.copy()

            if 'grading_mode' in config:
                exercise['grading_mode'] = config.pop('grading_mode')

            parent.append(exercise)
            if not config['category'] in category_keys:
                category_keys.append(config['category'])

        for config_file in [e.yaml_write for e in doc.traverse(aplus_nodes.html) if e.has_yaml('exercisecollection')]:
            config = yaml_writer.read(config_file)
            exercise = {
                'key': config['key'],
                'max_points': config.get('max_points', 0),
                'points_to_pass': config.get('points_to_pass', 0),
                'target_url': config['target_url'],
                'target_category': config['target_category'],
                'category': config['category'],
                'status': config.get('status', 'unlisted'),
                'title': config['title'],
            }
            parent.append(exercise)
            if not config['category'] in category_keys:
                category_keys.append(config['category'])


        category = 'chapter'
        for name,hidden,child in traverse_tocs(app, doc):
            meta = first_meta(child)
            status = 'hidden' if 'hidden' in meta else (
                'unlisted' if hidden else 'ready'
            )
            chapter = {
                'status': status,
                'name': first_title(child),
                'static_content': name + '.html',
                'category': category,
                'use_wide_column': app.config.use_wide_column,
                'children': [],
            }
            # If the chapter RST file is in a nested directory under the module
            # directory (e.g., module01/material/chapter.rst instead of
            # module01/chapter.rst), then the chapter key must contain parts of
            # the nested directory names in order to be unique within the module.
            # Different directories could contain files with the same names.
            key_parts = name.split('/')
            chapter['key'] = '_'.join(key_parts[1:])

            if meta:
                audience = meta.get('audience')
                if audience:
                    chapter['audience'] = audience
            if category in override:
                chapter.update(override[category])
            parent.append(chapter)
            if not 'chapter' in category_keys:
                category_keys.append('chapter')
            parse_chapter(name, child, chapter['children'], module_meta)

    # Read title from document.
    if not course_title:
        course_title = first_title(root)

    # Traverse the documents using toctree directives.
    title_date_re = re.compile(r'.*\(DL (.+)\)')
    for docname,hidden,doc in traverse_tocs(app, root):
        title = first_title(doc)
        title_date_match = title_date_re.match(title)
        meta = first_meta(doc)
        status = 'hidden' if 'hidden' in meta else (
            'unlisted' if hidden else 'ready'
        )
        read_open_src = meta.get('read-open-time', None)
        open_src = meta.get('open-time', course_open)
        close_src = meta.get('close-time', title_date_match.group(1) if title_date_match else course_close)
        late_src = meta.get('late-time', course_late)
        introduction = meta.get('introduction', None)
        module = {
            # modules01/index -> modules01
            # modules/01/index -> modules_01
            # modules/01/n/index -> modules_01_n
            # ...
            'key': docname if '/' not in docname else '_'.join(docname.split('/')[:-1]),
            'status': status,
            'name': title,
            'points_to_pass': meta.get('points-to-pass', 0),
            'children': [],
        }

        if read_open_src:
            module['read-open'] = parse_date(read_open_src)
        if open_src:
            module['open'] = parse_date(open_src)
        if close_src:
            module['close'] = parse_date(close_src)
        if late_src:
            module['late_close'] = parse_date(late_src)
            module['late_penalty'] = parse_float(meta.get('late-penalty', course_penalty), 0.0)
        if introduction is not None:
            module['introduction'] = introduction
        modules.append(module)
        parse_chapter(docname, doc, module['children'], meta)

    # Create categories.
    category_names = app.config.category_names
    categories = {
        key: {
            'name': category_names.get(key, key),
        } for key in category_keys
    }
    for key in ['chapter', 'feedback']:
        if key in categories:
            categories[key]['status'] = 'nototal'

    unprotected_paths = course_meta.get('unprotected-paths', app.config.unprotected_paths)
    if isinstance(unprotected_paths, str):
        unprotected_paths = shlex.split(unprotected_paths)
        logger.info(f'Parsed unprotected-paths: {unprotected_paths}')

    # Build configuration index.
    index = {
        'name': course_title,
        'static_dir': get_static_dir(app),
        'modules': modules,
        'categories': categories,
        'unprotected_paths': unprotected_paths,
        'configures': app.config.course_configures,
    }
    index['lang'] = language if language else app.config.language

    course_enrollment_start = course_meta.get('enrollment-start')
    course_enrollment_end = course_meta.get('enrollment-end')
    course_lifesupport_time = course_meta.get('lifesupport-time')
    course_archive_time = course_meta.get('archive-time')

    if course_open:
        index['start'] = parse_date(course_open)
    if course_close:
        index['end'] = parse_date(course_close)
    if course_enrollment_start is not None:
        # None check separates the cases:
        # 1) user inputs an empty value and it should be set into the YAML,
        # 2) user does not define any value and no value should be set in YAML
        index['enrollment_start'] = parse_date(course_enrollment_start, True)
    if course_enrollment_end is not None:
        index['enrollment_end'] = parse_date(course_enrollment_end, True)
    if course_lifesupport_time is not None:
        index['lifesupport_time'] = parse_date(course_lifesupport_time, True)
    if course_archive_time is not None:
        index['archive_time'] = parse_date(course_archive_time, True)

    if course_meta.get('view-content-to'):
        index['view_content_to'] = course_meta.get('view-content-to')
    if course_meta.get('enrollment-audience'):
        index['enrollment_audience'] = course_meta.get('enrollment-audience')
    if course_meta.get('index-mode'):
        index['index_mode'] = course_meta.get('index-mode')
    if course_meta.get('content-numbering'):
        index['content_numbering'] = course_meta.get('content-numbering')
    if course_meta.get('module-numbering'):
        index['module_numbering'] = course_meta.get('module-numbering')
    if course_meta.get('numerate-ignoring-modules') is not None:
        index['numerate_ignoring_modules'] = \
            True if course_meta.get('numerate-ignoring-modules', False) not in (
                False, 'false', 'False', 'no', 'No'
            ) else False
    head_urls = course_meta.get('course-head-urls', app.config.course_head_urls)
    if head_urls is not None:
        # If the value is None, it is not set to the index.yaml nor aplus-json at all.
        # If the value is an empty list, it is still part of the index.yaml
        # and could be used to override a previous truthy value.
        if isinstance(head_urls, str):
            # convert to a list and remove empty strings
            head_urls = list(filter(None, head_urls.split('\n')))
        index['head_urls'] = head_urls

    if course_meta.get('course-description') is not None:
        index['course_description'] = course_meta.get('course-description')
    if course_meta.get('course-footer') is not None:
        index['course_footer'] = course_meta.get('course-footer')

    return index


def append_manual_content(app, index):

    def recursive_merge(config, append):
        if type(append) == dict:
            for key,val in append.items():
                if not key in config:
                    config[key] = val
                else:
                    recursive_merge(config[key], append[key])
        elif type(append) == list:
            for entry in append:
                add = True
                if 'key' in entry:
                    for old in config:
                        if 'key' in old and old['key'] == entry['key']:
                            recursive_merge(old, entry)
                            add = False
                if add:
                    config.append(entry)

    for path in app.config.append_content:
        recursive_merge(index, yaml_writer.read(path))


def traverse_tocs(app, doc):
    names = []
    for toc in doc.traverse(addnodes.toctree):
        hidden = toc.get('hidden', False)
        for _,docname in toc.get('entries', []):
            names.append((docname,hidden))
    return [(name,hidden,app.env.get_doctree(name)) for name,hidden in names]
