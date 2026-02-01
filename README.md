# Django Transcription Starter

[![Discord](https://dcbadge.vercel.app/api/server/xWRaCDBtW4?style=flat)](https://discord.gg/xWRaCDBtW4)

This sample demonstrates interacting with the Deepgram API from Django to transcribe prerecorded audio files. It uses the Deepgram Python SDK with a frontend built from web components.

## What is Deepgram?

[Deepgram's](https://deepgram.com/) voice AI platform provides APIs for speech-to-text, text-to-speech, and full speech-to-speech voice agents. Over 200,000+ developers use Deepgram to build voice AI products and features.

## Sign-up to Deepgram

Before you start, it's essential to generate a Deepgram API key to use in this project. [Sign-up now for Deepgram and create an API key](https://console.deepgram.com/signup?jump=keys).

## Quickstart

<!--
### Using Deepgram CLI (Recommended)

The Deepgram CLI (`deepctl`) reads commands from `deepgram.toml` and handles setup automatically.

```bash
# Install Deepgram CLI
npm install -g @deepgram/cli

# Initialize and run
deepctl init    # Initialize submodules, create venv, install dependencies, setup .env
deepctl build   # Build frontend for production
deepctl dev     # Start development server at http://localhost:8080
```
-->

### Using Make (Recommended)

```bash
# Clone the repository
git clone https://github.com/deepgram-starters/django-transcription.git
cd django-transcription

# Initialize and install all dependencies
make init

# Build the frontend
make build

# Start the development server
make dev
```

The application will be available at http://localhost:8080.

**Other make commands:**
- `make start` - Start production server
- `make clean` - Remove venv, node_modules, and build artifacts
- `make update` - Update frontend submodule to latest
- `make status` - Show git and submodule status

### Manual Setup

If you prefer not to use Make:

```bash
# Clone and setup
git clone https://github.com/deepgram-starters/django-transcription.git
cd django-transcription

# Initialize submodules
git submodule update --init --recursive

# Create Python virtual environment
python3 -m venv venv

# Install backend dependencies
./venv/bin/pip install -r requirements.txt

# Install frontend dependencies
cd frontend && pnpm install && cd ..

# Setup environment
cp sample.env .env
# Edit .env and add your DEEPGRAM_API_KEY

# Build frontend
cd frontend && pnpm build && cd ..

# Start development server
./venv/bin/python app.py runserver 8080
```

The application will be available at http://localhost:8080.

## Development

This project uses:
- **Backend**: Django (single-file app with settings.configure())
- **Frontend**: Vite + Web Components (in `frontend/` submodule)
- **Port**: 8080 (both dev and production)

### Frontend Development

The frontend is a git submodule. To update it:

```bash
make update  # or: git submodule update --remote --merge
```

### Project Structure

```
django-transcription/
├── app.py                 # Django application (single-file)
├── deepgram.toml          # Deepgram CLI configuration
├── Makefile               # Make commands
├── requirements.txt       # Python dependencies
├── sample.env             # Environment template
├── .env                   # Your API keys (git-ignored)
└── frontend/              # Frontend submodule
    ├── src/               # Source files
    ├── dist/              # Built files (served by Django)
    └── package.json       # Frontend dependencies
```

## Issue Reporting

If you have found a bug or if you have a feature request, please report them at this repository issues section. Please do not report security vulnerabilities on the public GitHub issue tracker. The [Security Policy](./SECURITY.md) details the procedure for contacting Deepgram.

## Getting Help

We love to hear from you so if you have questions, comments or find a bug in the project, let us know! You can either:

- [Open an issue in this repository](https://github.com/deepgram-starters/django-transcription/issues/new)
- [Join the Deepgram Github Discussions Community](https://github.com/orgs/deepgram/discussions)
- [Join the Deepgram Discord Community](https://discord.gg/xWRaCDBtW4)

## Author

[Deepgram](https://deepgram.com)

## License

This project is licensed under the MIT license. See the [LICENSE](./LICENSE) file for more info.
