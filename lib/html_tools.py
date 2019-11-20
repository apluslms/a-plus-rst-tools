import fnmatch
import io, os, re

import yaml


def rewrite_outdir(out_dir, chapter_dirs, static_host):
    build_dir = os.path.dirname(out_dir)
    if static_host and not static_host.endswith('/'):
        static_host += '/'
    for path in _walk(build_dir):
        rewrite_file_links(path, out_dir, chapter_dirs, static_host)


def rewrite_file_links(path, root, chapter_dirs, static_host):
    content = _read_file(path)
    link_elements = [
        ('a', 'href'),
    ]
    other_elements = [
        ('img', 'src'),
        ('script', 'src'),
        ('iframe', 'src'),
        ('link', 'href'),
        ('video', 'poster'),
        ('source', 'src'),
    ]
    if path.endswith(".yaml"):
        # YAML files are handled separately because rewriting links with
        # a regexp could add YAML syntax errors to the file if quotes are not
        # escaped properly. Escaping is now taken care of by the YAML module.
        yaml_data_dict = yaml.load(content)
        recursive_rewrite_links(
            yaml_data_dict,
            path,
            root,
            link_elements,
            other_elements,
            static_host,
            chapter_dirs,
            'data-aplus-chapter ',
            'data-aplus-path="/static/{course}" ',
        )
        content = yaml.dump(yaml_data_dict, default_flow_style=False)
    else:
        content = rewrite_links(
            content,
            path,
            root,
            link_elements,
            other_elements,
            static_host,
            chapter_dirs,
            'data-aplus-chapter ',
            'data-aplus-path="/static/{course}" ',
        )
    _write_file(path, content)


def rewrite_links(content, path, root, link_elements, other_elements,
                    static_host, chapter_dirs, chapter_append, yaml_append):
    q1 = re.compile(r'^(\w+:|#)')
    q2 = re.compile(r'^(' + '|'.join(chapter_dirs) + r')(/|\\)')
    for tag, attr in link_elements:
        content = rewrite_elements(content, tag, attr, path, root,
                                    q1, static_host, q2, chapter_append, yaml_append)
    for tag, attr in other_elements:
        content = rewrite_elements(content, tag, attr, path, root,
                                    q1, static_host, None, None, yaml_append)
    return content


def rewrite_elements(content, tag, attr, path, root, q1, static_host, q2, append,
                    yaml_append):
    dir_name = os.path.dirname(path)
    out = ""
    p = re.compile(
        r'<' + tag + r'\s+[^<>]*'
        r'(?P<attr>' + attr + r')=(?P<slash>\\?)"(?P<val>[^"?#]*)'
    )
    i = 0
    for m in p.finditer(content):
        val = m.group('val')
        if val and not q1.search(val):

            # Add content up to attribute.
            j = m.start('attr')
            out += content[i:j]
            i = j

            full = ''
            if path.endswith('.yaml'):
                # content in yaml file
                if val.startswith('../'):
                    # targeting a static file or a chapter in a different round
                    full = os.path.realpath(os.path.join(root, val[3:]))
                elif not val.startswith('/'):
                    # targeting a file under the same round
                    # exercise YAML files use names according to the pattern roundkey_chapter_exercisekey.yaml
                    parts = os.path.basename(path).split('_', 1)
                    if len(parts) > 1:
                        round_key = parts[0]
                        full = os.path.realpath(os.path.join(root, round_key, val))
            else:
                # content in html file
                # dir_name points to either _build/html or _build/html/<round>
                full = os.path.realpath(os.path.join(dir_name, val))

            if full.startswith(root): # NB: root ends with "_build/html"
                my_path = full[len(root)+1:]

                # Links to chapters.
                if q2 and q2.search(my_path):
                    #a = append.replace('"','\\"') if m.group('slash') else append
                    if not out.endswith(append):
                        split_path = my_path.split('/')
                        module_path = '../' + split_path[0]
                        # If the chapter RST file is in a nested directory under
                        # the module directory (e.g., module01/material/chapter.rst
                        # instead of module01/chapter.rst), then the chapter key
                        # contains parts of the nested directory names in order
                        # to be unique within the module.
                        chapter_key = '_'.join(split_path[1:])
                        # Remove language postfix (_en, _fi), if any.
                        if chapter_key[-3] == '_':
                            chapter_key = chapter_key[:-3]
                        modified_path = module_path + '/' + chapter_key
                        j = m.start('val')
                        out += append + content[i:j] + modified_path.replace('\\', '/')
                        i = m.end('val')

                # Other links.
                elif static_host:
                    j = m.start('val')
                    out += content[i:j] + static_host + my_path.replace('\\','/')
                    i = m.end('val')

                elif dir_name.endswith('yaml') and yaml_append and not out.endswith(yaml_append):
                    # Sphinx sets URLs to local files as relative URLs that work in
                    # the local filesystem (e.g., ../_images/myimage.png).
                    # The A+ frontend converts the URLs correctly when they are in
                    # the chapter content. (The URL must be converted to an absolute
                    # URL that refers to the MOOC grader course static files.)
                    # However, the conversion does not work for URLs in exercise
                    # descriptions because unlike for chapters, the service URL of
                    # an exercise does not refer to the course static files.
                    # Therefore, we add the attribute data-aplus-path="/static/{course}"
                    # that A+ frontend uses to set the correct URL path.
                    # Unfortunately, we must hardcode the MOOC grader static URL
                    # (/static) here.
                    out += yaml_append

    out += content[i:]
    return out


def _walk(html_dir):
    files = []
    for root, dirnames, filenames in os.walk(html_dir):
        for filename in fnmatch.filter(filenames, '*.html'):
            files.append(os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, '*.yaml'):
            files.append(os.path.join(root, filename))
    return files


def _read_file(file_path):
    with io.open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def _write_file(file_path, content):
    with io.open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def recursive_rewrite_links(data_dict, path, root, link_elements, other_elements,
        static_host, chapter_dirs, chapter_append, yaml_append):
    '''Rewrite links in the string values inside the data_dict.'''
    # YAML file may have a list or a dictionary in the topmost level.
    if isinstance(data_dict, dict):
        for key, val in data_dict.items():
            if isinstance(val, dict) or isinstance(val, list):
                recursive_rewrite_links(val, path, root, link_elements,
                    other_elements, static_host, chapter_dirs, chapter_append,
                    yaml_append)
            elif isinstance(val, str):
                data_dict[key] = rewrite_links(val, path, root, link_elements,
                    other_elements, static_host, chapter_dirs, chapter_append,
                    yaml_append)

    elif isinstance(data_dict, list):
        for i, a in enumerate(data_dict):
            if isinstance(a, dict) or isinstance(a, list):
                recursive_rewrite_links(a, path, root, link_elements,
                    other_elements, static_host, chapter_dirs,
                    chapter_append, yaml_append)
            elif isinstance(a, str):
                data_dict[i] = rewrite_links(a, path, root, link_elements,
                    other_elements, static_host, chapter_dirs,
                    chapter_append, yaml_append)
