import re, os
from docutils import nodes
from sphinx import addnodes
from sphinx.errors import SphinxError

import aplus_nodes
import yaml_writer
import directives.meta
import html_tools


def prepare(app):
    ''' Prepares environment for configuration values. '''
    yaml_writer.create_directory(app)


def write(app, exception):
    ''' Writes the table of contents level configuration. '''
    if exception:
        return

    course_title = app.config.course_title
    course_open = app.config.course_open_date
    course_close = app.config.course_close_date
    override = app.config.override

    modules = []
    category_keys = []

    def traverse_tocs(doc):
        names = []
        for toc in doc.traverse(addnodes.toctree):
            hidden = toc.attributes['hidden']
            for _,docname in toc.get('entries', []):
                names.append((docname,hidden))
        return [(name,hidden,app.env.get_doctree(name)) for name,hidden in names]

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
                    u'content_expire_minutes': config.get(u'content_expire_minutes', 0),
                }
            exercise.update({
                u'allow_assistant_grading': False,
                u'status': u'unlisted',
            })
            if u'scale_points' in config:
                exercise[u'max_points'] = config.pop(u'scale_points')
            parent.append(exercise)
            if not config[u'category'] in category_keys:
                category_keys.append(config[u'category'])

        category = u'chapter'
        for name,hidden,child in traverse_tocs(doc):
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

    root = app.env.get_doctree(app.config.master_doc)
    if not course_title:
        course_title = first_title(root)

    # Traverse the documents using toctree directives.
    app.info('Traverse document elements to write configuration index.')
    title_date_re = re.compile(r'.*\(DL (.+)\)')
    for docname,hidden,doc in traverse_tocs(root):
        title = first_title(doc)
        title_date_match = title_date_re.match(title)
        meta = first_meta(doc)
        status = u'hidden' if 'hidden' in meta else (
            u'unlisted' if hidden else u'ready'
        )
        open_src = meta.get('open-time', course_open)
        close_src = meta.get('close-time', title_date_match.group(1) if title_date_match else course_close)
        module = {
            u'key': docname.split(u'/')[0],
            u'status': status,
            u'name': title,
            u'children': [],
        }
        if open_src:
            module[u'open'] = parse_date(open_src)
        if close_src:
            module[u'close'] = parse_date(close_src)
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
            categories[key][u'status'] = u'hidden'

    # Get relative out dir.
    i = 0
    while i < len(app.outdir) and i < len(app.confdir) and app.outdir[i] == app.confdir[i]:
        i += 1
    outdir = app.outdir.replace("\\", "/")
    if outdir[i] == '/':
        i += 1
    outdir = outdir[i:]

    # Write the configuration index.
    config = {
        u'name': course_title,
        u'language': app.config.language,
        u'static_dir': outdir,
        u'modules': modules,
        u'categories': categories,
    }
    if course_open:
        config[u'start'] = parse_date(course_open)
    if course_close:
        config[u'end'] = parse_date(course_close)

    # Append directly configured content.
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
        recursive_merge(config, yaml_writer.read(path))

    yaml_writer.write(yaml_writer.file_path(app.env, 'index'), config)

    # Mark links to other modules.
    app.info('Retouch all files to append chapter link attributes.')
    keys = [m['key'] for m in modules]
    keys.extend(['toc', 'user', 'account'])
    for html_file in html_tools.walk(os.path.dirname(app.outdir)):
        html_tools.annotate_file_links(
            html_file,
            [u'a'],
            [u'href'],
            keys,
            u'data-aplus-chapter="yes" '
        )
