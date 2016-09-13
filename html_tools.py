import fnmatch
import io, os, re


def annotate_links(content, file_name, tags, attributes, link_paths, append):
    dir_name = os.path.dirname(file_name)
    out = ""
    p = re.compile(
        r'<(' + '|'.join(tags) + r')[^<>]*'
        r'(?P<attr>' + r'|'.join(attributes) + r')="(?P<val>[^"]*)"'
    )
    q1 = re.compile(r'^(\w+:|#)')
    q2 = re.compile(r'(\/|\\)(' + '|'.join(link_paths) + r')(\/|\\)')
    i = 0
    for m in p.finditer(content):
        val = m.group('val')
        if not q1.search(val):
            full = os.path.realpath(os.path.join(dir_name, val))
            if q2.search(full):
                j = m.start('attr')
                out += content[i:j]
                i = j
                if not out.endswith(append):
                    out += append
    out += content[i:]
    return out


def walk(html_dir):
    html_files = []
    for root, dirnames, filenames in os.walk(html_dir):
        for filename in fnmatch.filter(filenames, '*.html'):
            html_files.append(os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, '*.yaml'):
            html_files.append(os.path.join(root, filename))
    return html_files


def _read_file(file_path):
    with io.open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def _write_file(file_path, content):
    with io.open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def annotate_file_links(html_file, tags, attributes, link_paths, append):
    content = _read_file(html_file)
    content = annotate_links(content, html_file, tags, attributes, link_paths, append)
    _write_file(html_file, content)
