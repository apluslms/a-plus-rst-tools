from sphinx.errors import SphinxError


translations = {
    'submit': {
        'en': 'Submit',
        'fi': u'Lähetä',
    },
    'submit_placeholder': {
        'en': 'A+ presents the exercise submission form here.',
        'fi': u'A+ esittää tässä kohdassa tehtävän palautuslomakkeen.',
    },
    'feedback': {
        'en': 'Feedback',
        'fi': 'Palaute',
    },
    'exercise': {
        'en': 'Exercise',
        'fi': u'Tehtävä',
    },
    'question': {
        'en': 'Question',
        'fi': 'Kysymys',
    },
    'agreement4': {
        'en': 'strongly agree',
        'fi': u'täysin samaa mieltä',
    },
    'agreement3': {
        'en': 'agree',
        'fi': u'jokseenkin samaa mieltä',
    },
    'agreement2': {
        'en': 'disagree',
        'fi': u'jokseenkin eri mieltä',
    },
    'agreement1': {
        'en': 'strongly disagree',
        'fi': u'täysin eri mieltä',
    },
    'agreement0': {
        'en': 'cannot say / no comments',
        'fi': 'en osaa sanoa / en kommentoi',
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
            d[l] += postfix
        return d

    return translations[key]
