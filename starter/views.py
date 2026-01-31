"""
Django Transcription Starter - Views

Simple function-based views for transcription API.
"""

import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from deepgram import DeepgramClient
from dotenv import load_dotenv
import toml

load_dotenv()

# Load API key
API_KEY = os.environ.get("DEEPGRAM_API_KEY")
if not API_KEY:
    raise ValueError("DEEPGRAM_API_KEY environment variable is required")

# Initialize Deepgram client
deepgram = DeepgramClient(api_key=API_KEY)

DEFAULT_MODEL = "nova-3"


@csrf_exempt
@require_http_methods(["POST"])
def transcribe(request):
    """
    POST /stt/transcribe

    Accepts file upload or URL for transcription.
    """
    try:
        # Get model from POST data
        model = request.POST.get('model', DEFAULT_MODEL)

        # Check for file upload
        file = request.FILES.get('file')
        url = request.POST.get('url')

        if not file and not url:
            return JsonResponse({
                "error": {
                    "type": "ValidationError",
                    "code": "INVALID_INPUT",
                    "message": "Either 'file' or 'url' must be provided"
                }
            }, status=400)

        # Transcribe
        if url:
            # URL transcription
            response = deepgram.listen.rest.v("1").transcribe_url(
                {"url": url},
                {"model": model, "smart_format": True}
            )
        else:
            # File transcription
            file_content = file.read()
            response = deepgram.listen.rest.v("1").transcribe_file(
                {"buffer": file_content},
                {"model": model, "smart_format": True}
            )

        # Format response
        result = response.results.channels[0].alternatives[0]
        metadata = response.metadata

        formatted_response = {
            "transcript": result.transcript or "",
        }

        # Add optional fields
        if hasattr(result, 'words') and result.words:
            formatted_response["words"] = [
                {
                    "text": word.word,
                    "start": word.start,
                    "end": word.end,
                    "speaker": getattr(word, 'speaker', None)
                }
                for word in result.words
            ]

        if metadata and hasattr(metadata, 'duration'):
            formatted_response["duration"] = metadata.duration

        formatted_response["metadata"] = {
            "model_uuid": getattr(metadata, 'model_uuid', None),
            "request_id": getattr(metadata, 'request_id', None),
            "model_name": model,
        }

        return JsonResponse(formatted_response)

    except Exception as e:
        print(f"Transcription error: {e}")
        return JsonResponse({
            "error": {
                "type": "TranscriptionError",
                "code": "TRANSCRIPTION_FAILED",
                "message": "Transcription failed. Please try again."
            }
        }, status=500)


@require_http_methods(["GET"])
def metadata(request):
    """
    GET /api/metadata

    Returns metadata from deepgram.toml
    """
    try:
        with open('deepgram.toml', 'r') as f:
            config = toml.load(f)

        if 'meta' not in config:
            return JsonResponse({
                'error': 'INTERNAL_SERVER_ERROR',
                'message': 'Missing [meta] section in deepgram.toml'
            }, status=500)

        return JsonResponse(config['meta'])

    except FileNotFoundError:
        return JsonResponse({
            'error': 'INTERNAL_SERVER_ERROR',
            'message': 'deepgram.toml file not found'
        }, status=500)

    except Exception as e:
        print(f"Error reading metadata: {e}")
        return JsonResponse({
            'error': 'INTERNAL_SERVER_ERROR',
            'message': f'Failed to read metadata: {str(e)}'
        }, status=500)
