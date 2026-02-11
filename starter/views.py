"""Django Transcription Starter - Views"""
import functools
import os
import json
import secrets
import time

import jwt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from deepgram import DeepgramClient
from dotenv import load_dotenv
import toml

load_dotenv()
API_KEY = os.environ.get("DEEPGRAM_API_KEY")
if not API_KEY:
    raise ValueError("DEEPGRAM_API_KEY required")
deepgram = DeepgramClient(api_key=API_KEY)

# ============================================================================
# SESSION AUTH - JWT tokens for production security
# ============================================================================

SESSION_SECRET = os.environ.get("SESSION_SECRET") or secrets.token_hex(32)
JWT_EXPIRY = 3600  # 1 hour


# Read frontend/dist/index.html for serving (production only)
_index_html_template = None
try:
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist", "index.html")) as f:
        _index_html_template = f.read()
except FileNotFoundError:
    pass  # No built frontend (dev mode)


def require_session(f):
    """Decorator that validates JWT from Authorization header."""
    @functools.wraps(f)
    def decorated(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse({
                "error": {
                    "type": "AuthenticationError",
                    "code": "MISSING_TOKEN",
                    "message": "Authorization header with Bearer token is required",
                }
            }, status=401)
        token = auth_header[7:]
        try:
            jwt.decode(token, SESSION_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return JsonResponse({
                "error": {
                    "type": "AuthenticationError",
                    "code": "INVALID_TOKEN",
                    "message": "Session expired, please refresh the page",
                }
            }, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({
                "error": {
                    "type": "AuthenticationError",
                    "code": "INVALID_TOKEN",
                    "message": "Invalid session token",
                }
            }, status=401)
        return f(request, *args, **kwargs)
    return decorated


# ============================================================================
# SESSION ROUTES - Auth endpoints (unprotected)
# ============================================================================

def serve_index(request):
    """Serve index.html (production only)."""
    if not _index_html_template:
        return HttpResponse("Frontend not built. Run make build first.", status=404)
    return HttpResponse(_index_html_template, content_type="text/html")


def get_session(request):
    """Issues a JWT session token."""
    token = jwt.encode(
        {"iat": int(time.time()), "exp": int(time.time()) + JWT_EXPIRY},
        SESSION_SECRET,
        algorithm="HS256",
    )
    return JsonResponse({"token": token})


# ============================================================================
# API ROUTES - Define your API endpoints here
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
@require_session
def transcribe(request):
    """POST /api/transcription"""
    try:
        # Extract file and URL from request (form data)
        file = request.FILES.get("file")
        url = request.POST.get("url")
        model = request.POST.get("model", "nova-3")

        # Validate input - must have either file or URL
        if not file and not url:
            return JsonResponse({
                "error": {
                    "type": "ValidationError",
                    "code": "INVALID_INPUT",
                    "message": "Either 'file' or 'url' must be provided"
                }
            }, status=400)

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
            return JsonResponse({
                "error": {
                    "type": "TranscriptionError",
                    "code": "NO_RESULTS",
                    "message": "No transcription results returned from Deepgram"
                }
            }, status=500)

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
        return JsonResponse({
            "error": {
                "type": "TranscriptionError",
                "code": "TRANSCRIPTION_FAILED",
                "message": str(error)
            }
        }, status=500)

@require_http_methods(["GET"])
def metadata(request):
    """GET /api/metadata"""
    try:
        with open('deepgram.toml', 'r') as f:
            return JsonResponse(toml.load(f).get('meta', {}))
    except:
        return JsonResponse({'error': 'Failed'}, status=500)
