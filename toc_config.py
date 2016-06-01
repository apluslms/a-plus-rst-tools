from sphinx import addnodes
from docutils import nodes
import yaml_writer


def prepare(app):
    ''' Prepares environment for configuration values. '''
    yaml_writer.create_directory(app)
    app.env.aplus = {}
    app.env.aplus['exercises'] = {}


def store_exercise(env, docname, data_dict):
    ''' Stores exercise data for higher level configuration. '''
    if not docname in env.aplus['exercises']:
        env.aplus['exercises'][docname] = []
    env.aplus['exercises'][docname].append(data_dict)


def write(app, exception):
    ''' Writes the table of contents level configuration. '''
    if exception:
        return
    modules = []
    categories = []

    def traverse_tocs(doc):
        names = []
        for toc in doc.traverse(addnodes.toctree):
            for _,docname in toc.get('entries', []):
                names.append(docname)
        return [(name,app.env.get_doctree(name)) for name in names]

    def first_title(doc):
        titles = doc.traverse(nodes.title)
        return titles[0].astext() if titles else 'Unnamed'

    # Recursive chapter parsing.
    def parse_chapter(docname, doc, parent):

        if docname in app.env.aplus['exercises']:
            for config in app.env.aplus['exercises'][docname]:
                exercise = {
                    'key': config['key'],
                    'config': config['key'] + '.yaml',
                    'max_submissions': 100, # TODO option
                    'max_points': config['max_points'],
                    'allow_assistant_grading': True, # TODO config
                    'status': 'unlisted',
                    'category': config['category'], # TODO the category
                }
                parent.append(exercise)

        for name,child in traverse_tocs(doc):
            chapter = {
                'key': name.split('/')[-1],
                'name': first_title(child),
                'static_content': name + '.html',
                'category': 'chapter', # TODO the category
                'children': [],
            }
            parent.append(chapter)
            parse_chapter(name, child, chapter['children'])

    # Traverse the documents using toctree directives.
    root = app.env.get_doctree(app.config.master_doc)
    for docname,doc in traverse_tocs(root):
        title = first_title(doc)
        module = {
            'key': docname.split('/')[0],
            'name': title,
            'open': None, # TODO from config
            'close': None, # TODO from title
            'children': [],
        }
        modules.append(module)
        parse_chapter(docname, doc, module['children'])

    # Get relative out dir.
    i = 0
    while i < len(app.outdir) and i < len(app.confdir) and app.outdir[i] == app.confdir[i]:
        i += 1
    if app.outdir[i] == '/':
        i += 1
    outdir = app.outdir[i:]

    # Write the configuration index.
    yaml_writer.write(
        yaml_writer.file_path(app.env, 'index'),
        {
            'static_dir': outdir,
            'start': None, # TODO from config
            'end': None, # TODO from config
            'modules': modules,
            'categories': categories,
        }
    )
