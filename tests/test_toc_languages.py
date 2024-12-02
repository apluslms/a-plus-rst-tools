# test_toc_languages.py
#
# Unit tests for lib/toc_languages.py

import logging
from pathlib import Path
import sys
from testfixtures import LogCapture
import unittest

# A hack to import code from the parent directory.
# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

import lib.toc_languages

from sphinx.errors import SphinxError

# Mock classes for testing IndexJoiner
class MockConfig:
    def __init__(self):
        self.skip_language_inconsistencies = False

class MockApp:
    def __init__(self):
        self.config = MockConfig()

# Tests lib/toc_languages.py
class TestTocLanguages(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app = MockApp()
        base_lang = 'foo'
        base = dict()
        cls.joiner = lib.toc_languages.IndexJoiner(app, base_lang, base)
        cls.logger = logging.getLogger('lib.toc_languages')
        print("logger initialized")

    def test_key_without_language(self):
        """
        Tests IndexJoiner.key_without_language()
        """
        kwl = self.__class__.joiner.key_without_language

        # Strip the beginning of a key string:
        # If the original string is "en_something" and the language
        # tag is "en", then the result is "something".
        self.assertEqual(kwl("en", "en_something"), "something")

        # Replace a language in the middle of a key string with an underscore
        self.assertEqual(kwl("en", "foo_en_something"), "foo_something")

        # String end of a key string
        self.assertEqual(kwl("en", "something_en"), "something")

        # Don't modify a key string without a language id.
        self.assertEqual(kwl("en", "something"), "something")

        # Don't modify a key string which begins with a language tag
        # but there is no separator.
        self.assertEqual(kwl("en", "entropy"), "entropy")
        self.assertEqual(kwl("en", "ingen"), "ingen")
        self.assertEqual(kwl("en", "benign"), "benign")

        # Remove all occurrences of a language id
        self.assertEqual(kwl("en", "en_foo_en_something_en"),
            "foo_something")

        # Dashes should work as separators as well, but they are replaced
        # with underscores in the middle of the string.
        self.assertEqual(kwl("en", "en-foo-en-something-en"),
            "foo_something")

        # Mixed dashes and underscores are processed as similar characters.
        self.assertEqual(kwl("en", "en_foo_en-something-en"),
            "foo_something")

        # Other language ids than "en" should work.
        self.assertEqual(kwl("se", "se_foo_se_something_se"),
            "foo_something")

    def test_join_keys(self):
        """
        Tests IndexJoiner.join_keys()
        """
        join_keys = self.__class__.joiner.join_keys
        logger = self.__class__.logger

        path = ['modules', '1', '2', '3']
        # Equal keys are passed without modifications
        self.assertEqual(join_keys(
            "en", "sorting_en_mergesort_mergesort_ex",
            "", "sorting_en_mergesort_mergesort_ex", path),
            "sorting_en_mergesort_mergesort_ex")

        # Keys with different language ids are matched
        self.assertEqual(join_keys(
            "en", "sorting_en_mergesort_mergesort_ex",
            "fi", "sorting_fi_mergesort_mergesort_ex", path),
            "sorting_mergesort_mergesort_ex", )

        # Mismatching keys produce a log message with the original keys.
        expected_log = (
            "sphinx.lib.toc_languages WARNING\n"
            "  Mismatching keys at modules.1.2.3:\n"
            "Language: en Key: sorting_en_something\n"
            "Language: fi Key: sorting_fi_different"
        )
        with LogCapture() as logs:
            result = join_keys("en", "sorting_en_something", "fi",
            "sorting_fi_different", path)
            self.assertEqual(str(logs), expected_log)
