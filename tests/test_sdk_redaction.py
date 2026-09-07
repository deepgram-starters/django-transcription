import json
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DEEPGRAM_API_KEY", "test-api-key")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
from deepgram.core import ApiError
from django.test import Client

django.setup()

from starter import views


class SdkRedactionTest(unittest.TestCase):
    def test_api_error_redacts_authorization_value(self):
        marker = "synthetic-api-key"
        error = ApiError(headers={"Authorization": f"Token {marker}"})

        self.assertNotIn(marker, str(error))

    def test_api_error_response_hides_upstream_details(self):
        error = ApiError(
            headers={"dg-project-id": "project-id"},
            status_code=401,
            body={"err_msg": "invalid API key"},
        )

        with self.assertLogs("starter.views", level="ERROR") as logs:
            client = Client()
            token = json.loads(client.get("/api/session").content)["token"]
            with patch.object(
                views.deepgram.listen.v1.media,
                "transcribe_url",
                side_effect=error,
            ):
                response = client.post(
                    "/api/transcription",
                    {"url": "https://example.com/audio.wav"},
                    HTTP_AUTHORIZATION=f"Bearer {token}",
                )

        self.assertEqual(
            json.loads(response.content),
            {
                "error": {
                    "type": "TranscriptionError",
                    "code": "TRANSCRIPTION_FAILED",
                    "message": "Deepgram request failed (HTTP 401)",
                }
            },
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("HTTP 401", logs.output[0])
        self.assertIn("invalid API key", logs.output[0])
        self.assertNotIn("dg-project-id", response.content.decode())
        self.assertNotIn("invalid API key", response.content.decode())
