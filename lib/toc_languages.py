from sphinx.errors import SphinxError
from sphinx.util import logging

import lib.yaml_writer as yaml_writer


logger = logging.getLogger(__name__)


# Following keys may be given a default in base (first) language
# and other language versions are allowed to omit them.

ACCEPTED_INDEX_DEFAULT_KEYS = [
    'description', 'contact', 'contact_phone', 'assistants',
    'start', 'end', 'static_dir', 'numerate_ignoring_modules',
    'module_types', 'exercise_types',
]
ACCEPTED_CATEGORY_DEFAULT_KEYS = [
    'status', 'points_to_pass',
]
ACCEPTED_MODULE_DEFAULT_KEYS = [
    'status', 'type', 'points_to_pass',
    'open', 'close', 'duration', 'late_close', 'late_duration', 'late_penalty',
]
ACCEPTED_CHILDREN_DEFAULT_KEYS = [
    'status', 'type', 'category', 'config', 'static_content',
    'max_submissions', 'max_points', 'points_to_pass',
    'min_group_size', 'max_group_size',
    'allow_assistant_viewing', 'allow_assistant_grading',
    'use_wide_column', 'generate_table_of_contents',
]
IDENTICAL_EXERCISE_KEYS = [
    'category', 'max_points', 'difficulty', 'max_submissions',
    'min_group_size', 'max_group_size', 'points_to_pass', 'feedback',
]
# Internal keys that may be joined in the |i18n format. Internal keys are only
# used inside the a-plus-rst-tools to pass information forward.
INTERNAL_KEYS_TO_JOIN = ['_rst_srcpath']


def join(app, indexes):
    base_lang,base = indexes[0]
    if len(indexes) < 2:
        return base
    joiner = IndexJoiner(app, base_lang, base)
    for lang,index in indexes[1:]:
        joiner.join(lang, index)
    return joiner.get_joined()


class IndexJoiner:

    def __init__(self, app, base_lang, base):
        self.app = app
        self.base_lang = base_lang
        self.joined = base
        self.joined['lang'] = [base_lang]
        self.errors = 0
        self.skip_errors = app.config.skip_language_inconsistencies

    def get_joined(self):
        if self.errors > 0:
            msg = "Language versions have previously reported {:d} inconsistencies!".format(self.errors)
            if self.app.config.skip_language_inconsistencies:
                logger.warning(msg + (
                    " The 'skip_language_inconsistencies' option is set and"
                    " therefore incomplete version of the course is compiled."
                    " This setting should only be used in development phase!"
                ))
            else:
                raise SphinxError(msg + " Fix the problems to compile the course.")
        return self.joined

    def join(self, lang2, index2):
        lang1 = self.base_lang
        index1 = self.joined
        path = []
        index = {}
        self.require_identical_dict_keys(path, lang1, index1, lang2, index2, ACCEPTED_INDEX_DEFAULT_KEYS)
        for k,v in index1.items():
            if k == 'lang':
                index[k] = v + [lang2]
            elif k == 'name':
                index[k] = join_values(lang1, v, lang2, index2.get(k, v))
            elif k == 'categories':
                p = path + ['categories']
                index[k] = self.join_categories(p, lang1, v, lang2, index2.get(k, {}))
            elif k == 'modules':
                p = path + ['modules']
                index[k] = self.join_modules(p, lang1, v, lang2, index2.get(k, []))
            elif deep_equals(v, index2.get(k, v)):
                index[k] = v
            else:
                self.raise_unequal(path, lang2, k)
        self.joined = index

    def join_categories(self, path, lang1, c1_map, lang2, c2_map):
        c_map = {}
        self.require_identical_dict_keys(path, lang1, c1_map, lang2, c2_map)
        for n,c1 in c1_map.items():
            c2 = c2_map.get(n, {})
            c_path = path + [n]
            c = {}
            self.require_identical_dict_keys(c_path, lang1, c1, lang2, c2, ACCEPTED_CATEGORY_DEFAULT_KEYS)
            for k,v in c1.items():
                if k == 'name':
                    c[k] = join_values(lang1, v, lang2, c2.get(k, v))
                elif deep_equals(v, c2.get(k, v)):
                    c[k] = v
                else:
                    self.raise_unequal(c_path, lang2, k)
            c_map[n] = c
        return c_map

    def join_modules(self, path, lang1, m1_list, lang2, m2_list):
        m_list = []
        for i,m1 in enumerate(
            self.require_identical_list_len(path, lang1, m1_list, lang2, m2_list)
        ):
            m2 = m2_list[i]
            m_path = path + [str(i + 1)]
            m = {}
            self.require_identical_dict_keys(m_path, lang1, m1, lang2, m2, ACCEPTED_MODULE_DEFAULT_KEYS)
            for k,v in m1.items():
                if k == 'key':
                    m[k] = join_keys(lang1, v, lang2, m2.get(k, v))
                elif k in ('name', 'title'):
                    m[k] = join_values(lang1, v, lang2, m2.get(k, v))
                elif k == 'children':
                    m[k] = self.join_children(m_path, lang1, v, lang2, m2.get(k, []))
                elif deep_equals(v, m2.get(k, v)):
                    m[k] = v
                else:
                    self.raise_unequal(m_path, lang2, k)
            m_list.append(m)
        return m_list

    def join_children(self, path, lang1, c1_list, lang2, c2_list):
        c_list = []
        for i,c1 in enumerate(
            self.require_identical_list_len(path, lang1, c1_list, lang2, c2_list)
        ):
            c2 = c2_list[i]
            c_path = path + [str(i + 1)]
            c = {}
            self.require_identical_dict_keys(c_path, lang1, c1, lang2, c2, ACCEPTED_CHILDREN_DEFAULT_KEYS)
            key = join_keys(lang1, c1.get('key', ''), lang2, c2.get('key', ''))
            for k,v in c1.items():
                if k == 'key':
                    c[k] = key
                elif k in ('name', 'title', 'static_content'):
                    c[k] = join_values(lang1, v, lang2, c2.get(k, v))
                elif k == 'config':
                    e1 = yaml_writer.read(yaml_writer.file_path(self.app.env, v))
                    e2 = yaml_writer.read(yaml_writer.file_path(self.app.env, c2.get(k, v)))
                    yaml_writer.write(
                        yaml_writer.file_path(self.app.env, key),
                        self.join_exercises(key, lang1, e1, lang2, e2)
                    )
                    c[k] = key + '.yaml'
                elif k == 'children':
                    c[k] = self.join_children(c_path, lang1, v, lang2, c2.get(k, []))
                elif k in INTERNAL_KEYS_TO_JOIN:
                    c[k + '|i18n'] = join_values(lang1, v, lang2, c2.get(k, v))
                elif deep_equals(v, c2.get(k, v)):
                    c[k] = v
                else:
                    self.raise_unequal(c_path, lang2, k)
            c_list.append(c)
        return c_list

    def join_exercises(self, key, lang1, c1, lang2, c2):
        path = [key]
        c = {}
        for k,v in c1.items():
            if k == 'key':
                c[k] = key
            elif k == 'url':
                override = self.app.env.config.override.get(c1.get('category'), {})
                if k in override:
                    c[k] = override[k].format(key=key)
                else:
                    c[k] = join_keys(lang1, v, lang2, c2.get(k, v))
            elif k in IDENTICAL_EXERCISE_KEYS:
                if v != c2.get(k, v):
                    self.raise_unequal(path, lang2, k)
                c[k] = v
            else:
                self.join_exercise_values(path, k, c, lang1, c1, lang2, c2)
        return c

    def join_exercise_values(self, path, k, d, lang1, d1, lang2, d2):
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
                    self.join_exercise_values(path + [k], kk, dd, lang1, v1, lang2, v2)
                d[k] = dd
            elif has_identical_len_and_dict_keys(v1, v2):
                ll = []
                for i,vv in enumerate(v1):
                    dd = {}
                    pp = path + [k, str(i + 1)]
                    for kk in vv.keys():
                        self.join_exercise_values(pp, kk, dd, lang1, vv, lang2, v2[i])
                    ll.append(dd)
                d[k] = ll
            else:
                if v2 is None or deep_equals(v1, v2):
                    d[k] = v1
                else:
                    d[k + '|i18n'] = join_values(lang1, v1, lang2, v2)

    def require_identical_dict_keys(self, path, lang1, d1, lang2, d2, defaults=None):
        d1d2 = set(d1.keys()) - set(d2.keys()) - set(defaults or [])
        if len(d1d2) > 0:
            self.raise_error('Missing {:d} fields at {} in {}: {}'.format(
                len(d1d2),
                path_names(path, d1d2),
                lang2,
                ', '.join(d1d2)
            ))
        d2d1 = set(d2.keys()) - set(d1.keys())
        if len(d2d1) > 0:
            self.raise_error('Surplus {:d} fields at {} in {}: {}'.format(
                len(d2d1),
                path_names(path, d2d1),
                lang2,
                ', '.join(d2d1)
            ))
        return d1.items()

    def require_identical_list_len(self, path, lang1, l1, lang2, l2):
        d = len(l2) - len(l1)
        if d > 0:
            self.raise_error('Surplus {:d} elements at {} in {}: {}'.format(
                d,
                path_names(path),
                lang2,
                key_names(l2[-d:])
            ))
            return l1
        if d < 0:
            self.raise_error('Missing {:d} elements at {} in {}: {}'.format(
                -d,
                path_names(path),
                lang2,
                key_names(l1[d:])
            ))
            return  l1[:d]
        return l1

    def raise_unequal(self, path, lang, key):
        self.raise_error('Unequal field not accepted in {}: {}'.format(
            lang,
            path_names(path, key)
        ))

    def raise_error(self, msg):
        logger.warning(msg)
        self.errors += 1


def path_names(path, fields=None):
    if not fields:
        return '.'.join(path)
    if type(fields) not in (list, set):
        fields = [fields]
    return ' '.join('.'.join(path + [f]) for f in fields)


def key_names(elements):
    return ', '.join(str(e.get('key', '[missing key]')) for e in elements)


def key_without_language(lang, key):
    separators = ('_', '-')
    result = ""
    i = 0

    # Find segments where the language id is surrounded by separators (or end of string).
    # Exclude them and return the remaining string.
    while i < len(key):
        if key[i] in separators:
            end_index = i + len(lang) + 1
            if key[i+1:end_index] == lang:
                if end_index >= len(key):
                    break
                if key[end_index] in separators:
                    i = end_index
                    continue
        result += key[i]
        i += 1
    return result


def join_keys(lang1, key1, lang2, key2):
    if key1 == key2 or key2 == '':
        return key1

    key1 = key_without_language(lang1, key1)
    key2 = key_without_language(lang2, key2)

    if key1 != key2:
        raise SphinxError(
            "Corresponding RST file names must match in multilingual courses:\n"
            + key1 + "\n" + key2)

    return key1


def join_values(lang1, val1, lang2, val2):
    if type(val1) == dict and lang1 in val1:
        if type(val2) == dict and lang2 in val2:
            val1[lang2] = val2[lang2]
        else:
            val1[lang2] = val2
        return val1
    if val1 == val2:
        return val1
    return {
        lang1: val1,
        lang2: val2
    }


def has_identical_dict_keys(d1, d2):
    if not (type(d1) == type(d2) == dict):
        return False

    # Collect the keys of both dicts into sets and compare their differences.
    # Keys with and without the i18n suffix are considered identical.
    keys1 = set()
    for k in d1:
        if k.endswith('|i18n'):
            keys1.add(k[:-5])
        else:
            keys1.add(k)
    keys2 = set()
    for k in d2:
        if k.endswith('|i18n'):
            keys2.add(k[:-5])
        else:
            keys2.add(k)
    return len(keys1 ^ keys2) == 0


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
