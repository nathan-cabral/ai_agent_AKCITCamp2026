import unittest

from ui.location import format_location, search_municipalities


MUNICIPALITIES = (
    {"name": "São Paulo", "uf": "SP", "state": "São Paulo"},
    {"name": "São Paulo", "uf": "PR", "state": "Paraná"},
    {"name": "Goiânia", "uf": "GO", "state": "Goiás"},
)


class LocationSearchTests(unittest.TestCase):
    def test_search_ignores_accents_and_case(self):
        result = search_municipalities(MUNICIPALITIES, "GOIANIA")

        self.assertEqual(result[0]["name"], "Goiânia")
        self.assertEqual(format_location(result[0]), "Goiânia — GO")

    def test_keeps_homonymous_municipalities_distinct_by_uf(self):
        all_matches = search_municipalities(MUNICIPALITIES, "sao paulo")
        parana_match = search_municipalities(MUNICIPALITIES, "sao paulo", "PR")

        self.assertEqual({item["uf"] for item in all_matches}, {"SP", "PR"})
        self.assertEqual(parana_match[0]["uf"], "PR")

    def test_returns_no_results_when_name_does_not_match(self):
        self.assertEqual(search_municipalities(MUNICIPALITIES, "不存在"), [])


if __name__ == "__main__":
    unittest.main()
