import re
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
        return titles[0].astext() if titles else 'Unnamed'

    def first_meta(doc):
        metas = doc.traverse(directives.meta.aplusmeta)
        return metas[0].options if metas else {}

    # Tries to parse date from natural text.
    def parse_date(src):
        parts = src.split(' ', 1)
        d = parts[0]
        t = parts[1] if len(parts) > 1 else ''
        if re.match('^\d\d.\d\d.\d\d\d\d$', d):
            ds = d.split('.')
            d = ds[2] + '-' + ds[1] + '-' + ds[0]
        elif not re.match('^\d\d\d\d-\d\d-\d\d$', d):
            raise SphinxError('Invalid date ' + d)
        if not re.match('^\d\d(:\d\d(:\d\d)?)?$', t):
            t = '12:00'
        return d + ' ' + t

    # Recursive chapter parsing.
    def parse_chapter(docname, doc, parent):
        for config_file in [e.yaml_write for e in doc.traverse(aplus_nodes.html) if e.has_yaml('exercise')]:
            config = yaml_writer.read(config_file)
            if config.get('_external', False):
                exercise = config.copy()
                del exercise['_external']
            else:
                exercise = {
                    'key': config['key'],
                    'config': config['key'] + '.yaml',
                    'max_submissions': config['max_submissions'],
                    'max_points': config.get('max_points', 0),
                    'difficulty': config.get('difficulty', ''),
                    'points_to_pass': config['points_to_pass'],
                    'category': config['category'],
                    'min_group_size': config['min_group_size'],
                    'max_group_size': config['max_group_size'],
                }
            exercise.update({
                'allow_assistant_grading': False,
                'status': 'unlisted',
            })
            if 'scale_points' in config:
                exercise['max_points'] = config['scale_points']
            parent.append(exercise)
            if not config['category'] in category_keys:
                category_keys.append(config['category'])

        for name,hidden,child in traverse_tocs(doc):
            meta = first_meta(child)
            chapter = {
                'key': name.split('/')[-1],#name.replace('/', '_'),
                'status': 'unlisted' if hidden else 'ready',
                'name': first_title(child),
                'static_content': name + '.html',
                'category': 'chapter',
                'use_wide_column': app.config.use_wide_column,
                'children': [],
            }
            if meta:
                audience = meta.get('audience')
                if audience:
                    chapter['audience'] = audience
            parent.append(chapter)
            if not 'chapter' in category_keys:
                category_keys.append('chapter')
            parse_chapter(name, child, chapter['children'])

    root = app.env.get_doctree(app.config.master_doc)
    if not course_title:
        course_title = first_title(root)

    # Traverse the documents using toctree directives.
    app.info('Traverse document elements to write configuration index.')
    title_date_re = re.compile('.*\(DL (.+)\)')
    for docname,hidden,doc in traverse_tocs(root):
        title = first_title(doc)
        title_date_match = title_date_re.match(title)
        meta = first_meta(doc)
        open_src = meta.get('open-time', course_open)
        close_src = meta.get('close-time', title_date_match.group(1) if title_date_match else course_close)
        module = {
            'key': docname.split('/')[0],
            'status': 'unlisted' if hidden else 'ready',
            'name': title,
            'children': [],
        }
        if open_src:
            module['open'] = parse_date(open_src)
        if close_src:
            module['close'] = parse_date(close_src)
        modules.append(module)
        parse_chapter(docname, doc, module['children'])

    # Create categories.
    category_names = app.config.category_names
    categories = {
        key: {
            'name': category_names.get(key, key),
        } for key in category_keys
    }
    for key in ['chapter', 'feedback']:
        if key in categories:
            categories[key]['status'] = 'hidden'

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
        'name': course_title,
        'language': app.config.language,
        'static_dir': outdir,
        'modules': modules,
        'categories': categories,
    }
    if course_open:
        config['start'] = parse_date(course_open)
    if course_close:
        config['end'] = parse_date(course_close)

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
    app.info('Retouch all HTML files to append chapter link attributes.')
    keys = [m['key'] for m in modules]
    keys.extend(['toc', 'user', 'account'])
    for html_file in html_tools.walk(app.outdir):
        html_tools.annotate_file_links(
            html_file,
            ['a'],
            ['href'],
            keys,
            'data-aplus-chapter="yes" '
        )
