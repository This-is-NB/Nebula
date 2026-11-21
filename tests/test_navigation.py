import unittest

from pysurf.navigation import resolve_address


class AddressResolutionTests(unittest.TestCase):
    def test_domain_defaults_to_https(self):
        result = resolve_address("example.com")

        self.assertEqual(result.toString(), "https://example.com")

    def test_plain_text_is_encoded_as_search(self):
        result = resolve_address("hello browser")

        self.assertEqual(
            result.toString(),
            "https://www.google.com/search?q=hello+browser",
        )

    def test_empty_input_uses_home(self):
        result = resolve_address("  ", home="https://example.org/")

        self.assertEqual(result.toString(), "https://example.org/")
