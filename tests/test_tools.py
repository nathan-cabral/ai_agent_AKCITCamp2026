import json
import tempfile
import unittest
from pathlib import Path

from agent.tools import save_draft_for_human_review
from case.schemas import CaseSummary


class SaveDraftForHumanReviewTests(unittest.TestCase):
    def test_saves_a_pending_review_draft_as_json(self) -> None:
        summary = CaseSummary(
            summary="Relato fictício para teste.",
            missing_information=["Data aproximada."],
            sources=[],
            requires_human_review=True,
        )

        with tempfile.TemporaryDirectory() as directory:
            draft_path = save_draft_for_human_review(summary, Path(directory))
            saved_draft = json.loads(draft_path.read_text(encoding="utf-8"))

        self.assertEqual(saved_draft["status"], "pending_human_review")
        self.assertEqual(saved_draft["case_summary"]["summary"], summary.summary)
        self.assertTrue(saved_draft["case_summary"]["requires_human_review"])
