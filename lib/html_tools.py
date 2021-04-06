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
        yaml_data_dict = yaml.safe_load(content)
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
            yaml_data_dict.get('_rst_srcpath|i18n', yaml_data_dict.get('_rst_srcpath')),
        )
        # _rst_srcpath is an internal value stored in the YAML file.
        # It is the path of the RST source file that contains the exercise.
        # The path is needed for fixing relative URLs, usually links pointing
        # to other chapters and exercises. It may have multiple values for
        # different languages in multilingual courses or only one string value
        # in monolingual courses.
        content = yaml.safe_dump(yaml_data_dict, default_flow_style=False,
            allow_unicode=True)
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
                    static_host, chapter_dirs, chapter_append, yaml_append,
                    rst_src_path=None):
    q1 = re.compile(r'^(\w+:|//|#)') # Starts with "https:", "//" or "#".
    q2 = re.compile(r'^(' + '|'.join(chapter_dirs) + r')(/|\\)') # Starts with a module directory name.
    for tag, attr in link_elements:
        content = rewrite_elements(content, tag, attr, path, root,
                                    q1, static_host, q2, chapter_append,
                                    yaml_append, rst_src_path)
    for tag, attr in other_elements:
        content = rewrite_elements(content, tag, attr, path, root,
                                    q1, static_host, None, None, yaml_append,
                                    rst_src_path)
    return content


def rewrite_elements(content, tag, attr, path, root, q1, static_host, q2, append,
                    yaml_append, rst_src_path=None):
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
                # rst_src_path: The RST source file path is needed for fixing
                # relative URLs in the exercise description.
                # It should have been saved in the YAML data by the exercise directive.
                if rst_src_path:
                    full = os.path.realpath(os.path.join(
                        root,
                        os.path.dirname(rst_src_path),
                        val
                    ))
                else:
                    # We don't know which directory the relative path starts from,
                    # so just assume the build root. It is likely incorrect.
                    full = os.path.realpath(os.path.join(root, val))
            else:
                # content in html file
                # dir_name points to either _build/html or _build/html/<round>
                full = os.path.realpath(os.path.join(dir_name, val))

            if full.startswith(root): # NB: root ends with "_build/html"
                val_path_from_root = full[len(root)+1:].replace('\\', '/')
                # Replace Windows path separator backslash to the forward slash.

                # Links to chapters.
                if q2 and q2.search(val_path_from_root):

                    if not out.endswith(append):
                        # Directory depth (starting from _build/html) of the source file
                        # that contains the link val.
                        if path.endswith('.yaml'):
                            # yaml files are always directly under _build/yaml,
                            # but A+ can fix the URL when we prepend "../" once.
                            # Most courses place chapters and exercises directly
                            # under the module directory, in which case one
                            # "../" is logical.
                            dir_depth = 1
                        else:
                            dir_depth = path[len(root)+1:].count(os.sep)

                        val_path_from_root = ('../' * dir_depth) + val_path_from_root
                        j = m.start('val')
                        out += append + content[i:j] + val_path_from_root
                        i = m.end('val')

                # Other links.
                elif static_host:
                    j = m.start('val')
                    out += content[i:j] + static_host + val_path_from_root
                    i = m.end('val')

                elif path.endswith('.yaml') and yaml_append and not out.endswith(yaml_append):
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
        static_host, chapter_dirs, chapter_append, yaml_append, rst_src_path,
        lang_key=False, lang=None):
    '''Rewrite links in the string values inside the data_dict.'''
    # YAML file may have a list or a dictionary in the topmost level.
    # lang_key and lang are used to pick the correct language from rst_src_path.
    if isinstance(data_dict, dict):
        for key, val in data_dict.items():
            if lang_key:
                # data_dict is the value for a key that had the ending "|i18n",
                # so now key is a language code.
                lang = key
            if isinstance(val, dict) or isinstance(val, list):
                recursive_rewrite_links(val, path, root, link_elements,
                    other_elements, static_host, chapter_dirs, chapter_append,
                    yaml_append, rst_src_path, key.endswith('|i18n'), lang)
                # lang_key: if key is, e.g., "title|i18n", then the val dict
                # contains keys like "en" and "fi".
            elif isinstance(val, str):
                if isinstance(rst_src_path, dict):
                    lang_rst_src_path = rst_src_path.get(lang if lang else 'en')
                else:
                    lang_rst_src_path = rst_src_path
                data_dict[key] = rewrite_links(val, path, root, link_elements,
                    other_elements, static_host, chapter_dirs, chapter_append,
                    yaml_append, lang_rst_src_path)

    elif isinstance(data_dict, list):
        for i, a in enumerate(data_dict):
            if isinstance(a, dict) or isinstance(a, list):
                recursive_rewrite_links(a, path, root, link_elements,
                    other_elements, static_host, chapter_dirs,
                    chapter_append, yaml_append, rst_src_path, lang_key, lang)
            elif isinstance(a, str):
                if isinstance(rst_src_path, dict):
                    lang_rst_src_path = rst_src_path.get(lang if lang else 'en')
                else:
                    lang_rst_src_path = rst_src_path
                data_dict[i] = rewrite_links(a, path, root, link_elements,
                    other_elements, static_host, chapter_dirs,
                    chapter_append, yaml_append, lang_rst_src_path)
