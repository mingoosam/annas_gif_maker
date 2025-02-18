# Anna's GIF Maker

A serverless application for creating GIFs from workout video segments, powered by AWS Lambda and FastAPI.

## Overview

This application processes workout videos to create GIFs of specific movements. It uses:
- OpenAI Whisper for audio transcription
- Fuzzy matching for movement detection
- MoviePy for GIF generation

The application is split into two main components:
1. A serverless API (Lambda + API Gateway) for handling uploads and user interactions
2. An EC2-based processing service for CPU-intensive video operations

## Architecture

```
                    ┌─────────────┐
                    │   Browser   │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  API Gateway │
                    └──────┬──────┘
                           │
         ┌─────────┬──────┴──────┬─────────┐
         │         │             │         │
    ┌────┴────┐   │   ┌─────┐   │    ┌────┴────┐
    │ Lambda  │   │   │ S3  │   │    │DynamoDB │
    └────┬────┘   │   └──┬──┘   │    └────┬────┘
         │        │      │      │         │
         └────────┼──────┼──────┼─────────┘
                  │      │      │
             ┌────┴──────┴──────┴────┐
             │      EventBridge      │
             └─────────┬─────────────┘
                       │
                  ┌────┴────┐
                  │   EC2   │
                  └─────────┘
```

## Features

- Upload workout videos
- Automatic movement detection using audio transcription
- GIF generation with customizable trim points
- Batch download of selected GIFs
- Auto-scaling processing capacity
- Automatic cleanup of temporary files

## Setup

1. Install the package:
```bash
pip install .
```

2. Configure AWS credentials:
```bash
aws configure
```

3. Deploy the infrastructure:
```bash
sam deploy -t template.yaml
```

## Environment Variables

Create a `.env` file with:
```
AWS_S3_BUCKET=your-bucket-name
AWS_STATUS_TABLE=your-table-name
AWS_EVENT_BUS=your-event-bus
```

## Development

The project uses `pyproject.toml` for dependency management. Main dependencies include:
- FastAPI for the web framework
- MoviePy for video processing
- OpenAI Whisper for transcription
- Boto3 for AWS integration
- Mangum for Lambda compatibility

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
│   ├── gif_generator.py
│   ├── ec2_processor.py  # AWS processing service
│   └── ec2_shutdown.py   # Auto-shutdown logic
├── config/
│   ├── config.py         # Application settings
│   └── aws_config.py     # AWS configuration
├── static/
│   ├── js/
│   └── css/
└── templates/
    └── index.html
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

None

## Author

Andy G. Varner
