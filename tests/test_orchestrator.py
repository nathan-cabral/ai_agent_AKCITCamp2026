import unittest

from agent.orchestrator import process_case_report


class ProcessCaseReportTests(unittest.TestCase):
    def test_returns_a_valid_summary_for_a_fictitious_report(self) -> None:
        result = process_case_report("Relato fictício: houve ameaças por mensagem.")

        self.assertEqual(result.summary, "Relato fictício: houve ameaças por mensagem.")
        self.assertEqual(result.sources, [])
        self.assertTrue(result.requires_human_review)
        self.assertGreater(len(result.missing_information), 0)

    def test_rejects_an_empty_report(self) -> None:
        with self.assertRaises(ValueError):
            process_case_report("   ")


if __name__ == "__main__":
    unittest.main()
