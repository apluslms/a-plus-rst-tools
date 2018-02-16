from sphinx.errors import SphinxError


def join(indexes):
    if len(indexes) < 2:
        return indexes[0][1]
    base_lang = indexes[0][0]
    join = indexes[0][1]
    for lang,index in indexes[1:]:
        join_index(base_lang, join, lang, index)
    return join


def join_index(lang1, index1, lang2, index2):

    def recursive_join(path, v1, v2):
        t1 = type(v1)
        t2 = type(v2)
        if t1 == dict and t2 == dict:
            for k,v in v1.items():
                p = path + [k]
                if not k in v2:
                    raise SphinxError('{} is in {} but not in {}'.format(
                        '.'.join(p), lang1, lang2
                    ))
                recursive_join(p, v, v2[k])
        elif t1 == list and t2 == list:
            if len(v1) != len(v2):
                raise SphinxError('{} has {:d} items in {} but {:d} items in {}'.format(
                    '.'.join(path), len(v1), lang1, len(v2), lang2
                ))
            for i,v in enumerate(v1):
                p = path + [str(i)]
                recursive_join(p, v, v2[i])
        elif v1 != v2:
            print('{} has different value in {} than in {}'.format(
                '.'.join(path), lang1, lang2
            ))

    recursive_join([], index1, index2)
