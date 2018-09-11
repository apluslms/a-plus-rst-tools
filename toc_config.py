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

    course_open = app.config.course_open_date
    course_close = app.config.course_close_date

    modules = []
    category_keys = []

    def traverse_tocs(doc):
        names = []
        for toc in doc.traverse(addnodes.toctree):
            for _,docname in toc.get('entries', []):
                names.append(docname)
        return [(name,app.env.get_doctree(name)) for name in names]

    def first_title(doc):
        titles = doc.traverse(nodes.title)
        return titles[0].astext() if titles else 'Unnamed'

    def first_meta(doc):
        metas = doc.traverse(directives.meta.meta)
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

    # 'exercise_docnames' dict is used to check for exercise key uniqueness.
    exercise_docnames = {}

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
                    'points_to_pass': config['points_to_pass'],
                    'category': config['category'],
                    'difficulty': config.get('difficulty', ''),
                }
            allow_assistant_viewing = config.get('allow_assistant_viewing', app.config.allow_assistant_viewing)
            allow_assistant_grading = config.get('allow_assistant_grading', app.config.allow_assistant_grading)
            exercise.update({
                'allow_assistant_grading': allow_assistant_grading,
                'allow_assistant_viewing': allow_assistant_viewing,
                'status': 'unlisted',
            })
            if 'scale_points' in config:
                exercise['max_points'] = config['scale_points']
            parent.append(exercise)
            if not config['category'] in category_keys:
                category_keys.append(config['category'])

            key = exercise['key']
            exercise_docnames[key] = exercise_docnames.get(key, []) + [docname]

        for name,child in traverse_tocs(doc):
            chapter = {
                'key': name.split('/')[-1],#name.replace('/', '_'),
                'name': first_title(child),
                'static_content': name + '.html',
                'category': 'chapter',
                'use_wide_column': app.config.use_wide_column,
                'children': [],
            }
            parent.append(chapter)
            if not 'chapter' in category_keys:
                category_keys.append('chapter')
            parse_chapter(name, child, chapter['children'])

    root = app.env.get_doctree(app.config.master_doc)
    course_title = first_title(root)

    # Traverse the documents using toctree directives.
    app.info('Traverse document elements to write configuration index.')
    title_date_re = re.compile('.*\(DL (.+)\)')
    for docname,doc in traverse_tocs(root):
        title = first_title(doc)
        title_date_match = title_date_re.match(title)
        meta = first_meta(doc)
        open_src = meta.get('open-time', course_open)
        close_src = meta.get('close-time', title_date_match.group(1) if title_date_match else course_close)
        late_close_src = meta.get('late-time', course_close)
        late_penalty_src = meta.get('late-penalty', 0.5)
        module = {
            'key': docname.split('/')[0],
            'name': title,
            'children': [],
        }
        if open_src:
            module['open'] = parse_date(open_src)
        if close_src:
            module['close'] = parse_date(close_src)
        if late_close_src:
            module['late_close'] = parse_date(late_close_src)
        if late_penalty_src:
            module['late_penalty'] = late_penalty_src
        modules.append(module)
        parse_chapter(docname, doc, module['children'])

    # Check for exercise uniqueness.
    nonunique_exercises = []
    for key in exercise_docnames:
        if len(exercise_docnames[key]) > 1:
            nonunique_exercises.append(key)

    if nonunique_exercises:
        violations = "\n"
        for key in nonunique_exercises:
            violations += "Exercise with key '{}' found in files {}\n".format(key, exercise_docnames[key])
        raise SphinxError('Exercise keys must be unique! {}'.format(violations))

    # Create categories.
    categories = {key: {'name': key} for key in category_keys}

    # Get relative out dir.
    i = 0
    while i < len(app.outdir) and i < len(app.confdir) and app.outdir[i] == app.confdir[i]:
        i += 1
    if app.outdir[i] == '/':
        i += 1
    outdir = app.outdir[i:]

    # Write the configuration index.
    config = {
        'name': course_title,
        #'language': app.config.language,
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
    for html_file in html_tools.walk(app.outdir):
        html_tools.annotate_file_links(
            html_file,
            ['href'],
            keys,
            'data-aplus-chapter="yes" '
        )
