# -*- coding: utf-8 -*-
from sphinx.errors import SphinxError


translations = {
    'submit': {
        'en': u'Submit',
        'fi': u'Lähetä',
    },
    'submit_placeholder': {
        'en': u'A+ presents the exercise submission form here.',
        'fi': u'A+ esittää tässä kohdassa tehtävän palautuslomakkeen.',
    },
        'active_element_placeholder': {
        'en': u'A+ presents the active element here.',
        'fi': u'A+ esittää tässä kohdassa "active element"-elementin.',
    },
    'feedback': {
        'en': u'Feedback',
        'fi': u'Palaute',
    },
    'exercise': {
        'en': u'Exercise',
        'fi': u'Tehtävä',
    },
    'question': {
        'en': u'Question',
        'fi': u'Kysymys',
    },
    'agreement4': {
        'en': u'strongly agree',
        'fi': u'täysin samaa mieltä',
    },
    'agreement3': {
        'en': u'agree',
        'fi': u'jokseenkin samaa mieltä',
    },
    'agreement2': {
        'en': u'disagree',
        'fi': u'jokseenkin eri mieltä',
    },
    'agreement1': {
        'en': u'strongly disagree',
        'fi': u'täysin eri mieltä',
    },
    'agreement0': {
        'en': u'cannot say / no comments',
        'fi': u'en osaa sanoa / en kommentoi',
    },
}


def get(env, key):
    if key not in translations:
        raise SphinxError('Unknown translation key {}'.format(key))

    lang = env.config.language or 'en'
    if lang not in translations[key]:
        raise SphinxError('Missing translation for {} and key {}'.format(lang, key))

    return translations[key][lang]


def opt(key, postfix=None):
    if key not in translations:
        raise SphinxError('Unknown translation key {}'.format(key))

    if postfix:
        d = translations[key].copy()
        for l in d.keys():
            d[l] = u"{} {}".format(d[l], postfix)
        return d

    return translations[key]
