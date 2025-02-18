# Anna's GIF Maker

A FastAPI application for creating GIFs from workout video segments.

## Overview

This application processes workout videos to create GIFs of specific movements. It uses:
- OpenAI Whisper for audio transcription
- Fuzzy matching for movement detection
- MoviePy for GIF generation

## Features

- Upload workout videos
- Automatic movement detection using audio transcription
- GIF generation with customizable trim points
- Batch download of selected GIFs
- Real-time processing progress updates
- Preview trimmed GIFs before download

## Setup

1. Install the package:
```bash
pip install .
```

2. Run the application:
```bash
uvicorn workout_processor.main:app --reload
```

## Environment Variables

Create a `.env` file with:
```
VIDEO_PATH=/path/to/default/video  # Optional
```

## Development

The project uses `pyproject.toml` for dependency management. Main dependencies include:
- FastAPI for the web framework
- MoviePy for video processing
- OpenAI Whisper for transcription
- Jinja2 for templating

To install development dependencies:
```bash
pip install -e ".[dev]"
```

Project structure:
```
src/workout_processor/
├── api/
│   └── routes.py          # FastAPI routes
├── core/
│   ├── processor.py       # Video processing logic
│   ├── audio.py          # Audio extraction
│   ├── transcription.py  # Whisper integration
│   ├── movement_detection.py
│   └── gif_generator.py
├── config/
│   └── config.py         # Application settings
├── static/
│   ├── js/              # Frontend JavaScript
│   └── css/             # Styling
└── templates/
    └── index.html       # Main application page
```

## Usage

1. Open the application in your browser (default: http://localhost:8000)
2. Upload a workout video
3. Enter movement names to detect
4. Process the video
5. Preview and trim the generated GIFs
6. Download selected GIFs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

None

## Author

Andy Varner