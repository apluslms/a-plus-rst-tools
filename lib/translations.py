# -*- coding: utf-8 -*-
from sphinx.errors import SphinxError


translations = {
    'submit': {
        'en': u'Submit',
        'fi': u'Lähetä',
        'sv': 'Skicka in',
    },
    'submit_placeholder': {
        'en': u'A+ presents the exercise submission form here.',
        'fi': u'A+ esittää tässä kohdassa tehtävän palautuslomakkeen.',
        'sv': 'A+ presenterar formuläret för inlämningen av uppgiften här.',
    },
        'active_element_placeholder': {
        'en': u'A+ presents the active element here.',
        'fi': u'A+ esittää tässä kohdassa "active element"-elementin.',
        'sv': 'A+ presenterar det aktiva elementet här.',
    },
    'feedback': {
        'en': u'Feedback',
        'fi': u'Palaute',
        'sv': 'Feedback',
    },
    'exercise': {
        'en': u'Exercise',
        'fi': u'Tehtävä',
        'sv': 'Uppgift',
    },
    'question': {
        'en': u'Question',
        'fi': u'Kysymys',
        'sv': 'Fråga',
    },
    'agreement4': {
        'en': u'strongly agree',
        'fi': u'täysin samaa mieltä',
        'sv': 'instämmer helt',
    },
    'agreement3': {
        'en': u'agree',
        'fi': u'jokseenkin samaa mieltä',
        'sv': 'instämmer delvis',
    },
    'agreement2': {
        'en': u'disagree',
        'fi': u'jokseenkin eri mieltä',
        'sv': 'instämmer inte',
    },
    'agreement1': {
        'en': u'strongly disagree',
        'fi': u'täysin eri mieltä',
        'sv': 'instämmer inte alls',
    },
    'agreement0': {
        'en': u'cannot say / no comments',
        'fi': u'en osaa sanoa / en kommentoi',
        'sv': 'jag kan inte säga / ingen kommentar',
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
