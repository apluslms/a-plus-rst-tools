import re, os
from docutils import nodes
from sphinx import addnodes
from sphinx.errors import SphinxError

import aplus_nodes
import directives.meta
import lib.yaml_writer as yaml_writer
import lib.html_tools as html_tools
import lib.toc_languages as toc_languages


def prepare(app):
    ''' Prepares environment for configuration values. '''
    yaml_writer.create_directory(app)


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
    tocs = root.traverse(addnodes.toctree)
    keys = set()
    if tocs and tocs[0].get('rawcaption') == u'Select language':
        app.info('Detected language tree.')

        indexes = []
        for docname,_,doc in traverse_tocs(app, root):
            i = docname.rfind('_')
            if i < 0:
                raise SphinxError('Language postfix is required (e.g. docname_en): ' + docname)
            lang = docname[(i + 1):]
            app.info('Traverse document elements to write configuration index ({}).'.format(lang))
            index = make_index(app, doc)
            yaml_writer.write(yaml_writer.file_path(app.env, 'index_' + lang), index)
            indexes.append((lang, index))

        app.info('Joining language tree to one index.')
        index = toc_languages.join(app, indexes)
        append_manual_content(app, index)
        yaml_writer.write(yaml_writer.file_path(app.env, 'index'), index)
        keys |= set(m['key'] for m in index['modules'])

    else:
        app.info('Traverse document elements to write configuration index.')
        index = make_index(app, root)
        append_manual_content(app, index)
        yaml_writer.write(yaml_writer.file_path(app.env, 'index'), index)
        keys |= set(m['key'] for m in index['modules'])

    # Rewrite links for remote inclusion.
    app.info('Retouch all files to rewrite links.')
    keys |= {'toc', 'user', 'account'}
    html_tools.rewrite_outdir(app.outdir, keys, app.config.static_host)


def make_index(app, root):

    course_title = app.config.course_title
    course_open = app.config.course_open_date
    course_close = app.config.course_close_date
    course_late = app.config.default_late_date
    course_penalty = app.config.default_late_penalty
    override = app.config.override

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
        titles = doc.traverse(nodes.title)
        return titles[0].astext() if titles else u'Unnamed'

    def first_meta(doc):
        metas = doc.traverse(directives.meta.aplusmeta)
        return metas[0].options if metas else {}

    # Tries to parse date from natural text.
    def parse_date(src):
        parts = src.split(u' ', 1)
        d = parts[0]
        t = parts[1] if len(parts) > 1 else ''
        if re.match(r'^\d\d.\d\d.\d\d\d\d$', d):
            ds = d.split('.')
            d = ds[2] + u'-' + ds[1] + u'-' + ds[0]
        elif not re.match(r'^\d\d\d\d-\d\d-\d\d$', d):
            raise SphinxError(u'Invalid date ' + d)
        if not re.match(r'^\d\d(:\d\d(:\d\d)?)?$', t):
            t = u'12:00'
        return d + u' ' + t

    def parse_float(src, default):
        return float(src) if src else default

    # Recursive chapter parsing.
    def parse_chapter(docname, doc, parent):
        for config_file in [e.yaml_write for e in doc.traverse(aplus_nodes.html) if e.has_yaml(u'exercise')]:
            config = yaml_writer.read(config_file)
            if config.get(u'_external', False):
                exercise = config.copy()
                del exercise[u'_external']
            else:
                exercise = {
                    u'key': config[u'key'],
                    u'config': config[u'key'] + u'.yaml',
                    u'max_submissions': config.get(u'max_submissions', 0),
                    u'max_points': config.get(u'max_points', 0),
                    u'difficulty': config.get(u'difficulty', ''),
                    u'points_to_pass': config.get(u'points_to_pass', 0),
                    u'category': config[u'category'],
                    u'min_group_size': config.get(u'min_group_size', 1),
                    u'max_group_size': config.get(u'max_group_size', 1),
                    u'confirm_the_level': config.get(u'confirm_the_level', False),
                }
            allow_assistant_viewing = config.get(u'allow_assistant_viewing', app.config.allow_assistant_viewing)
            allow_assistant_grading = config.get(u'allow_assistant_grading', app.config.allow_assistant_grading)
            exercise.update({
                u'status': u'unlisted',
                u'allow_assistant_viewing': allow_assistant_viewing,
                u'allow_assistant_grading': allow_assistant_grading,
            })
            if u'scale_points' in config:
                exercise[u'max_points'] = config.pop(u'scale_points')
            parent.append(exercise)
            if not config[u'category'] in category_keys:
                category_keys.append(config[u'category'])

        for config_file in [e.yaml_write for e in doc.traverse(aplus_nodes.html) if e.has_yaml(u'exercisecollection')]:
            config = yaml_writer.read(config_file)
            exercise = {
                u'key': config[u'key'],
                u'max_points': config[u'max_points'],
                u'points_to_pass': config.get(u'points_to_pass', 0),
                u'collection_course': config[u'collection_course'],
                u'collection_url': config[u'collection_url'],
                u'collection_category': config[u'collection_category'],
                u'category': config[u'category'],
                u'status': u'unlisted',
            }
            parent.append(exercise)
            if not config[u'category'] in category_keys:
                category_keys.append(config[u'category'])


        category = u'chapter'
        for name,hidden,child in traverse_tocs(app, doc):
            meta = first_meta(child)
            status = u'hidden' if 'hidden' in meta else (
                u'unlisted' if hidden else u'ready'
            )
            chapter = {
                u'key': name.split(u'/')[-1],#name.replace('/', '_'),
                u'status': status,
                u'name': first_title(child),
                u'static_content': name + u'.html',
                u'category': category,
                u'use_wide_column': app.config.use_wide_column,
                u'children': [],
            }
            if meta:
                audience = meta.get('audience')
                if audience:
                    chapter[u'audience'] = yaml_writer.ensure_unicode(audience)
            if category in override:
                chapter.update(override[category])
            parent.append(chapter)
            if not u'chapter' in category_keys:
                category_keys.append(u'chapter')
            parse_chapter(name, child, chapter[u'children'])

    # Read title from document.
    if not course_title:
        course_title = first_title(root)

    # Traverse the documents using toctree directives.
    title_date_re = re.compile(r'.*\(DL (.+)\)')
    for docname,hidden,doc in traverse_tocs(app, root):
        title = first_title(doc)
        title_date_match = title_date_re.match(title)
        meta = first_meta(doc)
        status = u'hidden' if 'hidden' in meta else (
            u'unlisted' if hidden else u'ready'
        )
        open_src = meta.get('open-time', course_open)
        close_src = meta.get('close-time', title_date_match.group(1) if title_date_match else course_close)
        late_src = meta.get('late-time', course_late)
        module = {
            # modules01/index -> modules01
            # modules/01/index -> modules_01
            # modules/01/n/index -> modules_01_n
            # ...
            u'key': docname if u'/' not in docname else u'_'.join(docname.split(u'/')[:-1]),
            u'status': status,
            u'name': title,
            u'points_to_pass': meta.get('points-to-pass', 0),
            u'children': [],
        }
        if open_src:
            module[u'open'] = parse_date(open_src)
        if close_src:
            module[u'close'] = parse_date(close_src)
        if late_src:
            module[u'late_close'] = parse_date(late_src)
            module[u'late_penalty'] = parse_float(meta.get('late-penalty', course_penalty), 0.0)
        modules.append(module)
        parse_chapter(docname, doc, module[u'children'])

    # Create categories.
    category_names = app.config.category_names
    categories = {
        key: {
            u'name': category_names.get(key, key),
        } for key in category_keys
    }
    for key in ['chapter', 'feedback']:
        if key in categories:
            categories[key][u'status'] = u'nototal'

    # Build configuration index.
    index = {
        u'name': course_title,
        u'language': app.config.language,
        u'static_dir': get_static_dir(app),
        u'modules': modules,
        u'categories': categories,
    }
    if course_open:
        index[u'start'] = parse_date(course_open)
    if course_close:
        index[u'end'] = parse_date(course_close)

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
