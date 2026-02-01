import os
import sys
import json
import toml

from deepgram import DeepgramClient
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import path
from django.utils.crypto import get_random_string
from dotenv import load_dotenv
from whitenoise import WhiteNoise

load_dotenv()

settings.configure(
    ALLOWED_HOSTS=["*"],
    DEBUG=(os.environ.get("DEBUG", "1") == "1"),
    ROOT_URLCONF=__name__,
    SECRET_KEY=get_random_string(40),
    MIDDLEWARE=[
        "whitenoise.middleware.WhiteNoiseMiddleware",
    ],
    STATIC_URL="/",
    STATIC_ROOT="frontend/dist/",
    STATICFILES_STORAGE="whitenoise.storage.CompressedManifestStaticFilesStorage",
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["frontend/dist"],
        },
    ],
)

# Initialize Deepgram client
API_KEY = os.environ.get("DEEPGRAM_API_KEY")
if not API_KEY:
    raise ValueError("DEEPGRAM_API_KEY required")
deepgram = DeepgramClient(api_key=API_KEY)


async def transcribe(request):
    if request.method == "POST":
        try:
            # Extract file and URL from request (form data)
            file = request.FILES.get("file")
            url = request.POST.get("url")
            model = request.POST.get("model", "nova-3")

            # Validate input - must have either file or URL
            if not file and not url:
                return json_abort("Either 'file' or 'url' must be provided")

            # Handle URL-based transcription
            if url:
                response = deepgram.listen.v1.media.transcribe_url(
                    url=url,
                    model=model,
                    smart_format=True,
                )
            # Handle file upload
            elif file:
                file_data = file.read()
                response = deepgram.listen.v1.media.transcribe_file(
                    request=file_data,
                    model=model,
                    smart_format=True,
                )

            # Access the results from the Deepgram response
            result = response.results.channels[0].alternatives[0]
            metadata = response.metadata

            if not result:
                return json_abort("No transcription results returned from Deepgram")

            # Build response object matching the contract
            transcription = {
                "transcript": result.transcript or "",
            }

            # Add optional fields if available
            if hasattr(result, 'words') and result.words:
                transcription["words"] = [
                    {
                        "text": word.word,
                        "start": word.start,
                        "end": word.end,
                    }
                    for word in result.words
                ]

            if metadata and hasattr(metadata, 'duration'):
                transcription["duration"] = metadata.duration

            # Add metadata
            transcription["metadata"] = {
                "model_uuid": metadata.model_uuid if hasattr(metadata, 'model_uuid') else None,
                "request_id": metadata.request_id if hasattr(metadata, 'request_id') else None,
                "model_name": model,
            }

            return JsonResponse(transcription)

        except Exception as error:
            print(f"Transcription error: {error}")
            return json_abort(str(error))
    else:
        return HttpResponseBadRequest("Invalid HTTP method")


def json_abort(message):
    return HttpResponseBadRequest(json.dumps({"err": str(message)}))


def index(request):
    return render(request, "index.html")


def metadata(request):
    """Return metadata from deepgram.toml"""
    try:
        with open('deepgram.toml', 'r') as f:
            config = toml.load(f)
        return JsonResponse(config.get('meta', {}))
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


urlpatterns = [
    path("", index),
    path("api/metadata", metadata, name="metadata"),
    path("stt/transcribe", transcribe, name="transcribe"),
]

app = get_wsgi_application()
app = WhiteNoise(app, root="frontend/dist/", prefix="/")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
