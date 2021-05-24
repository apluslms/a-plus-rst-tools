# -*- coding: utf-8 -*-
from sphinx.errors import SphinxError


translations = {
    'submit': {
        'en': 'Submit',
        'fi': 'Lähetä',
        #'sv': 'Skicka in',
    },
    'submit_placeholder': {
        'en': 'A+ presents the exercise submission form here.',
        'fi': 'A+ esittää tässä kohdassa tehtävän palautuslomakkeen.',
        #'sv': 'A+ presenterar formuläret för inlämningen av uppgiften här.',
    },
        'active_element_placeholder': {
        'en': 'A+ presents the active element here.',
        'fi': 'A+ esittää tässä kohdassa "active element"-elementin.',
        #'sv': 'A+ presenterar det aktiva elementet här.',
    },
    'feedback': {
        'en': 'Feedback',
        'fi': 'Palaute',
        #'sv': 'Feedback',
    },
    'exercise': {
        'en': 'Exercise',
        'fi': 'Tehtävä',
        #'sv': 'Uppgift',
    },
    'question': {
        'en': 'Question',
        'fi': 'Kysymys',
        #'sv': 'Fråga',
    },
    'agreement4': {
        'en': 'strongly agree',
        'fi': 'täysin samaa mieltä',
        #'sv': 'instämmer helt',
    },
    'agreement3': {
        'en': 'agree',
        'fi': 'jokseenkin samaa mieltä',
        #'sv': 'instämmer delvis',
    },
    'agreement2': {
        'en': 'disagree',
        'fi': 'jokseenkin eri mieltä',
        #'sv': 'instämmer inte',
    },
    'agreement1': {
        'en': 'strongly disagree',
        'fi': 'täysin eri mieltä',
        #'sv': 'instämmer inte alls',
    },
    'agreement0': {
        'en': 'cannot say / no comments',
        'fi': 'en osaa sanoa / en kommentoi',
        #'sv': 'jag kan inte säga / ingen kommentar',
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
            d[l] = "{} {}".format(d[l], postfix)
        return d

    return translations[key]
