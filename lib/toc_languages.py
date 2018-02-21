from sphinx.errors import SphinxError

import lib.yaml_writer as yaml_writer


def join(app, indexes):
    if len(indexes) < 2:
        return indexes[0][1]
    base_lang = indexes[0][0]
    join = indexes[0][1]
    join['language'] = [base_lang]
    for lang,index in indexes[1:]:
        join = join_index(app, base_lang, join, lang, index)
    return join


def join_index(app, lang1, index1, lang2, index2):
    path = []
    index = {}
    require_identical_dict_keys(path, lang1, index1, lang2, index2)
    for k,v in index1.items():
        if k == 'language':
            index[k] = v + [lang2]
        elif k == 'name':
            index[k] = join_values(lang1, v, lang2, index2[k])
        elif k == 'categories':
            p = path + ['categories']
            index[k] = join_categories(app, p, lang1, v, lang2, index2[k])
        elif k == 'modules':
            p = path + ['modules']
            index[k] = join_modules(app, p, lang1, v, lang2, index2[k])
        elif deep_equals(v, index2[k]):
            index[k] = v
        else:
            raise_unequal(path, lang2, k)
    return index


def join_categories(app, path, lang1, c1_map, lang2, c2_map):
    c_map = {}
    require_identical_dict_keys(path, lang1, c1_map, lang2, c2_map)
    for n,c1 in c1_map.items():
        c2 = c2_map[n]
        c_path = path + [n]
        c = {}
        require_identical_dict_keys(c_path, lang1, c1, lang2, c2)
        for k,v in c1.items():
            if k == 'name':
                c[k] = join_values(lang1, v, lang2, c2[k])
            elif deep_equals(v, c2[k]):
                c[k] = v
            else:
                raise_unequal(c_path, lang2, k)
        c_map[n] = c
    return c_map


def join_modules(app, path, lang1, m1_list, lang2, m2_list):
    m_list = []
    require_identical_list_len(path, lang1, m1_list, lang2, m2_list)
    for i,m1 in enumerate(m1_list):
        m2 = m2_list[i]
        m_path = path + [str(i + 1)]
        m = {}
        require_identical_dict_keys(m_path, lang1, m1, lang2, m2)
        for k,v in m1.items():
            if k == 'key':
                m[k] = join_keys(lang1, v, lang2, m2[k])
            elif k == 'name':
                m[k] = join_values(lang1, v, lang2, m2[k])
            elif k == 'children':
                m[k] = join_children(app, m_path, lang1, v, lang2, m2[k])
            elif deep_equals(v, m2[k]):
                m[k] = v
            else:
                raise_unequal(m_path, lang2, k)
        m_list.append(m)
    return m_list


def join_children(app, path, lang1, c1_list, lang2, c2_list):
    c_list = []
    require_identical_list_len(path, lang1, c1_list, lang2, c2_list)
    for i,c1 in enumerate(c1_list):
        c2 = c2_list[i]
        c_path = path + [str(i + 1)]
        c = {}
        require_identical_dict_keys(c_path, lang1, c1, lang2, c2)
        key = join_keys(lang1, c1.get('key', ''), lang2, c2.get('key', ''))
        for k,v in c1.items():
            if k == 'key':
                c[k] = key
            elif k in ('name', 'title', 'static_content'):
                c[k] = join_values(lang1, v, lang2, c2[k])
            elif k == 'config':
                e1 = yaml_writer.read(yaml_writer.file_path(app.env, v))
                e2 = yaml_writer.read(yaml_writer.file_path(app.env, c2[k]))
                yaml_writer.write(
                    yaml_writer.file_path(app.env, key),
                    join_exercises(app, key, lang1, e1, lang2, e2)
                )
                c[k] = key + '.yaml'
            elif k == 'children':
                c[k] = join_children(app, c_path, lang1, v, lang2, c2[k])
            elif deep_equals(v, c2[k]):
                c[k] = v
            else:
                raise_unequal(c_path, lang2, k)
        c_list.append(c)
    return c_list


def join_exercises(app, key, lang1, c1, lang2, c2):
    path = [key]
    c = {}
    for k,v in c1.items():
        if k == 'key':
            c[k] = key
        elif k == 'url':
            override = app.env.config.override.get(c1.get('category'), {})
            if k in override:
                c[k] = override[k].format(key=key)
            elif v != c2[k]:
                raise_unequal(path, lang2, k)
            else:
                c[k] = v
        elif k in (
            'category', 'max_points', 'difficulty', 'max_submissions',
            'min_group_size', 'max_group_size', 'points_to_pass', 'feedback',
        ):
            if v != c2[k]:
                raise_unequal(path, lang2, k)
            c[k] = v
        else:
            join_exercise_values(path, k, c, lang1, c1, lang2, c2)
    return c


def join_keys(lang1, key1, lang2, key2):
    k = ""
    l2 = len(key2)
    for i,c in enumerate(key1):
        if i < l2 and c == key2[i]:
            if not (c in ("_", "-")) or k == "" or k[-1] != c:
                k += c
    return k


def join_values(lang1, val1, lang2, val2):
    if type(val1) == dict and lang1 in val1:
        if type(val2) == dict and lang2 in val2:
            val1[lang2] = val2[lang2]
        else:
            val1[lang2] = val2
        return val1
    return {
        lang1: val1,
        lang2: val2
    }


def join_exercise_values(path, k, d, lang1, d1, lang2, d2):
    v1 = d1[k]
    if k.endswith('|i18n'):
        v2 = d2.get(k, d2.get(k[:-5]))
        if v2 is None:
            d[k] = v1
        else:
            d[k] = join_values(lang1, v1, lang2, v2)
    else:
        v2 = d2.get(k)
        if has_identical_dict_keys(v1, v2):
            dd = {}
            for kk in v1.keys():
                join_exercise_values(path + [k], kk, dd, lang1, v1, lang2, v2)
            d[k] = dd
        elif has_identical_len_and_dict_keys(v1, v2):
            ll = []
            for i,vv in enumerate(v1):
                dd = {}
                pp = path + [k, str(i + 1)]
                for kk in vv.keys():
                    join_exercise_values(pp, kk, dd, lang1, vv, lang2, v2[i])
                ll.append(dd)
            d[k] = ll
        else:
            if v2 is None or deep_equals(v1, v2):
                d[k] = v1
            else:
                d[k + '|i18n'] = join_values(lang1, v1, lang2, v2)


def require_identical_dict_keys(path, lang1, d1, lang2, d2, ignore=None):
    d1d2 = set(d1.keys()) - set(d2.keys()) - set(ignore or [])
    d2d1 = set(d2.keys()) - set(d1.keys()) - set(ignore or [])
    if len(d1d2) > 0:
        raise SphinxError('Missing fields in {}: {}'.format(
            lang2,
            path_names(path, d1d2)
        ))
    if len(d2d1) > 0:
        raise SphinxError('Surplus fields in {}: {}'.format(
            lang2,
            path_names(path, d2d1)
        ))


def require_identical_list_len(path, lang1, l1, lang2, l2):
    d = len(l2) - len(l1)
    if d > 0:
        raise SphinxError('Surplus {:d} elements in {}: {}'.format(
            d,
            lang2,
            path_names(path)
        ))
    if d < 0:
        raise SphinxError('Missing {:d} elements in {}: {}'.format(
            -d,
            lang2,
            path_names(path)
        ))


def has_identical_dict_keys(d1, d2):
    return (
        type(d1) == type(d2) == dict
        and len(set(d1.keys()) ^ set(d2.keys())) == 0
    )


def has_identical_len_and_dict_keys(l1, l2):
    if (
        not (type(l1) == type(l2) == list)
        or len(l1) != len(l2)
    ):
        return False
    for i,d1 in enumerate(l1):
        if not has_identical_dict_keys(d1, l2[i]):
            return False
    return True


def deep_equals(a, b):
    ta = type(a)
    tb = type(b)

    if ta == dict and tb == dict:
        if len(set(a.keys()) ^ set(b.keys())) > 0:
            return False
        for k,v in a.items():
            if not deep_equals(v, b[k]):
                return False

    elif ta == list and tb == list:
        if len(a) != len(b):
            return False
        for i,v in enumerate(a):
            if not deep_equals(v, b[i]):
                return False

    elif a != b:
        return False

    return True


def raise_unequal(path, lang, key):
    raise SphinxError('Unequal field in {}: {}'.format(
        lang,
        path_names(path, key)
    ))


def path_names(path, fields=None):
    if not fields:
        return '.'.join(path)
    if type(fields) not in (list, set):
        fields = [fields]
    return ' '.join('.'.join(path + [f]) for f in fields)
