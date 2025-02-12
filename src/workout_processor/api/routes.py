"""
API routes for the workout processor application.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse
from pathlib import Path
import shutil
import uuid
from typing import List
import json
from sse_starlette.sse import EventSourceResponse
from asyncio import Queue
import asyncio
from moviepy.editor import VideoFileClip
import tempfile
from fastapi import BackgroundTasks
from zipfile import ZipFile
from pydantic import BaseModel

from ..config.config import settings
from ..core.processor import WorkoutProcessor
from .models import ProcessingRequest, ProcessingResponse
from ..logger import logger

router = APIRouter()

# Store uploaded files temporarily
UPLOAD_DIR = Path("temp/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Add this at the top with other global variables
progress_queues = {}

class GifDownloadRequest(BaseModel):
    url: str
    start: float
    end: float

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Handle video file upload"""
    if not file.filename.lower().endswith(('.mov', '.mp4', '.avi')):
        raise HTTPException(400, "Unsupported file format")

    # Generate unique ID for this upload
    video_id = str(uuid.uuid4())
    video_path = UPLOAD_DIR / f"{video_id}{Path(file.filename).suffix}"

    try:
        with video_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    return {"video_id": video_id}


@router.get("/progress/{video_id}")
async def progress_stream(video_id: str):
    """Stream processing progress updates"""
    async def event_generator():
        if video_id not in progress_queues:
            progress_queues[video_id] = Queue()
        
        try:
            while True:
                message = await progress_queues[video_id].get()
                if message == "DONE":
                    break
                yield {
                    "event": "message",
                    "retry": 1000,
                    "data": json.dumps(message)
                }
        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())


@router.post("/process")
async def process_video(request: ProcessingRequest):
    """Process video with specified movements"""
    video_path = next(UPLOAD_DIR.glob(f"{request.video_id}.*"))
    
    # Create progress queue for this video
    progress_queues[request.video_id] = Queue()
    queue = progress_queues[request.video_id]

    # Temporarily override settings.MOVEMENTS
    original_movements = settings.MOVEMENTS
    settings.MOVEMENTS = request.movements

    try:
        # Update progress for each step
        await queue.put({"step": "audio", "progress": 0})
        processor = WorkoutProcessor(video_path, progress_callback=queue.put)
        result = await processor.process()
        
        # Add gif_path to each segment
        movements_with_paths = {}
        for i, (movement, segments) in enumerate(result["movements"].items(), 1):
            movements_with_paths[movement] = []
            for j, segment in enumerate(segments, 1):
                segment_with_path = dict(segment)
                segment_with_path["gif_path"] = f"{i:02d}_{movement.replace(' ', '_')}_{j:02d}.gif"
                movements_with_paths[movement].append(segment_with_path)
        
        # Signal completion
        await queue.put("DONE")
        
        response = ProcessingResponse(
            video_id=request.video_id,
            movements=movements_with_paths
        )
        
        return response
    finally:
        settings.MOVEMENTS = original_movements


@router.get("/download/{gif_path:path}")
async def download_gif(gif_path: str, start: float = None, end: float = None):
    """Download a specific GIF, optionally trimmed"""
    full_path = settings.GIFS_PATH / gif_path
    if not full_path.exists():
        raise HTTPException(404, "GIF not found")
    
    if start is not None and end is not None:
        try:
            # Load the GIF
            clip = VideoFileClip(str(full_path))
            
            # Adjust start and end times relative to GIF duration
            gif_duration = clip.duration
            relative_start = (start % gif_duration)
            relative_end = min(end % gif_duration, gif_duration)
            
            if relative_start >= relative_end:
                relative_end = gif_duration
            
            # Create trimmed version
            trimmed_clip = clip.subclip(relative_start, relative_end)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            
            # Save trimmed GIF
            trimmed_clip.write_gif(str(temp_path))
            
            # Clean up
            clip.close()
            trimmed_clip.close()
            
            # Create background task for cleanup
            async def cleanup():
                await asyncio.sleep(5)  # Wait a bit to ensure file has been sent
                try:
                    temp_path.unlink(missing_ok=True)
                except Exception as e:
                    logger.error(f"Failed to cleanup temporary file {temp_path}: {e}")
            
            background = BackgroundTasks()
            background.add_task(cleanup)
            
            return FileResponse(
                temp_path,
                headers={'Content-Disposition': f'attachment; filename="{gif_path}"'},
                background=background
            )
        except Exception as e:
            logger.error(f"Failed to trim GIF: {e}")
            # Fall back to original GIF
            return FileResponse(full_path)
    
    return FileResponse(full_path)

@router.post("/download-selected")
async def download_selected(gifs: List[GifDownloadRequest]):
    """Create a zip file of selected GIFs"""
    try:
        # Create temporary zip file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            zip_path = Path(temp_zip.name)
        
        # Create zip file with selected GIFs
        with ZipFile(zip_path, 'w') as zip_file:
            for gif in gifs:
                # Extract gif path and original filename from url
                gif_path = gif.url.split('/')[-1].split('?')[0]
                # Use the original filename (without any query parameters)
                output_filename = gif_path.split('?')[0]
                full_path = settings.GIFS_PATH / gif_path
                
                if not full_path.exists():
                    continue
                
                # Create trimmed GIF if needed
                if gif.start is not None and gif.end is not None:
                    clip = VideoFileClip(str(full_path))
                    
                    # Adjust times relative to GIF duration
                    gif_duration = clip.duration
                    relative_start = (gif.start % gif_duration)
                    relative_end = min(gif.end % gif_duration, gif_duration)
                    
                    if relative_start >= relative_end:
                        relative_end = gif_duration
                    
                    # Create trimmed version
                    trimmed_clip = clip.subclip(relative_start, relative_end)
                    
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as temp_file:
                        temp_path = Path(temp_file.name)
                        trimmed_clip.write_gif(str(temp_path))
                        clip.close()
                        trimmed_clip.close()
                        
                        # Add to zip with original filename
                        zip_file.write(temp_path, output_filename)
                        
                        # Clean up temp file
                        temp_path.unlink(missing_ok=True)
                else:
                    # Add original GIF to zip
                    zip_file.write(full_path, output_filename)
        
        # Create background task for cleanup
        async def cleanup():
            await asyncio.sleep(5)
            try:
                zip_path.unlink(missing_ok=True)
            except Exception as e:
                logger.error(f"Failed to cleanup zip file {zip_path}: {e}")
        
        background = BackgroundTasks()
        background.add_task(cleanup)
        
        return FileResponse(
            zip_path,
            media_type='application/zip',
            headers={'Content-Disposition': 'attachment; filename="selected_gifs.zip"'},
            background=background
        )
    except Exception as e:
        logger.error(f"Failed to create zip file: {e}")
        raise HTTPException(500, "Failed to create zip file") 