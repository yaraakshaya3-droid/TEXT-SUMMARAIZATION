import io
import unittest

from app import app


class AppRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_summarize_rejects_short_text(self):
        response = self.client.post(
            "/summarize",
            json={"text": "Too short to summarize well.", "length": "short"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Enter a longer passage", response.get_json()["error"])

    def test_summarize_accepts_text_file_upload(self):
        text = (
            "Artificial intelligence is transforming classrooms by helping teachers personalize lessons, "
            "spot learning gaps, and provide faster feedback to students. Schools are also exploring how "
            "AI can automate repetitive work so teachers can spend more time mentoring and planning. "
            "At the same time, educators are debating privacy, fairness, and the risk of students relying "
            "too heavily on machine-generated answers. Responsible use depends on clear policies, teacher "
            "training, and keeping human judgment at the center of decision-making."
        )

        response = self.client.post(
            "/summarize",
            data={
                "length": "short",
                "file": (io.BytesIO(text.encode("utf-8")), "sample.txt"),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("summary", payload)
        self.assertLess(payload["output_word_count"], payload["input_word_count"])


if __name__ == "__main__":
    unittest.main()
