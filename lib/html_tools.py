import fnmatch
import io, os, re



def rewrite_outdir(out_dir, chapter_dirs, static_host):
    build_dir = os.path.dirname(out_dir)
    if static_host and not static_host.endswith('/'):
        static_host += '/'
    for path in _walk(build_dir):
        rewrite_file_links(path, out_dir, chapter_dirs, static_host)


def rewrite_file_links(path, root, chapter_dirs, static_host):
    content = _read_file(path)
    content = rewrite_links(
        content,
        path,
        root,
        [
            (u'a',u'href'),
        ],
        [
            (u'img',u'src'),
            (u'script',u'src'),
            (u'iframe',u'src'),
            (u'link',u'href'),
            (u'video',u'poster'),
            (u'source',u'src'),
        ],
        static_host,
        chapter_dirs,
        u'data-aplus-chapter="yes" ',
    )
    _write_file(path, content)


def rewrite_links(content, path, root, link_elements, other_elements,
                    static_host, chapter_dirs, chapter_append):
    dir_name = os.path.dirname(path)
    q1 = re.compile(r'^(\w+:|#)')
    q2 = re.compile(r'^(' + '|'.join(chapter_dirs) + r')(/|\\)')
    for tag,attr in link_elements:
        content = rewrite_elements(content, tag, attr, dir_name, root,
                                    q1, static_host, q2, chapter_append)
    for tag,attr in other_elements:
        content = rewrite_elements(content, tag, attr, dir_name, root,
                                    q1, static_host, None, None)
    return content


def rewrite_elements(content, tag, attr, path, root, q1, static_host, q2, append):
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

            full = os.path.realpath(os.path.join(path, val))
            if full.startswith(root):
                my_path = full[len(root)+1:]

                # Links to chapters.
                if q2 and q2.search(my_path):
                    a = append.replace('"','\\"') if m.group('slash') else append
                    if not out.endswith(append):
                        out += append
                        #j = m.start('val')
                        #out += append + content[i:j] + my_path.replace('\\','/')
                        #i = m.end('val')

                # Other links.
                elif static_host:
                    j = m.start('val')
                    out += content[i:j] + static_host + my_path.replace('\\','/')
                    i = m.end('val')
                    
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

