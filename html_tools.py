import fnmatch
import io, os, re


def annotate_links(content, attributes, link_paths, append):
    out = ""
    p = re.compile(
        '(' + '|'.join(attributes) +
        ')="(/?|(../)*)(' + '|'.join(link_paths) + ')'
    )
    i = 0
    for m in p.finditer(content):
        out += content[i:m.start()]
        i = m.start()
        if not out.endswith(append):
            out += append
    out += content[i:]
    return out


def walk(html_dir):
    html_files = []
    for root, dirnames, filenames in os.walk(html_dir):
        for filename in fnmatch.filter(filenames, '*.html'):
            html_files.append(os.path.join(root, filename))
    return html_files


def _read_file(file_path):
    with io.open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def _write_file(file_path, content):
    with io.open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def annotate_file_links(html_file, attributes, link_paths, append):
    content = _read_file(html_file)
    content = annotate_links(content, attributes, link_paths, append)
    _write_file(html_file, content)
