import unittest

from services.summary_service import generate_summary, summary_is_meaningfully_shorter


class SummaryServiceTestCase(unittest.TestCase):
    def test_summary_is_shorter(self):
        original = (
            "Cities are adopting electric buses to reduce air pollution, lower fuel costs, and improve the "
            "overall reliability of public transportation. Many transit agencies are pairing fleet upgrades "
            "with charging infrastructure and route planning tools so the transition is practical as well "
            "as environmentally beneficial. Officials still need to address upfront costs, grid capacity, "
            "and long-term maintenance planning to scale adoption successfully."
        )
        summary = "Cities are adopting electric buses to cut pollution and costs, but scaling them still requires infrastructure and planning."

        self.assertTrue(summary_is_meaningfully_shorter(original, summary, "short"))

    def test_generate_summary_returns_compressed_output(self):
        text = (
            "Community health programs are expanding mobile clinics to reach rural patients who live far from "
            "hospitals and specialists. These clinics can deliver checkups, screenings, and follow-up care "
            "closer to where people live, which improves access and helps catch health issues earlier. "
            "However, long-term success depends on reliable funding, staffing, broadband access, and "
            "coordination with local providers."
        )

        result = generate_summary(text, "medium")

        self.assertIn("summary", result)
        self.assertLess(result["output_word_count"], result["input_word_count"])


if __name__ == "__main__":
    unittest.main()
