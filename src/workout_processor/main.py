from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .api.routes import router

app = FastAPI(title="Anna's GIF Maker")

# Mount static files
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# Setup templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Include API routes
app.include_router(router, prefix="/api")

# Root route
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request}) 