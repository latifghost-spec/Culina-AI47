"""
Simple backend without Gemini dependencies for testing Velo 3 video service
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from datetime import datetime

app = FastAPI(title="CulinaAI - Velo 3 Video Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import Velo 3 video service without Gemini dependencies
from services.velo3_video_service import velo3_video_service, VideoGenerationResult

class VideoGenerationRequest(BaseModel):
    chef_prompt: str
    menu_item: Optional[str] = None
    video_name: Optional[str] = None
    custom_settings: Optional[Dict[str, Any]] = None

class MenuItemVideoRequest(BaseModel):
    menu_item: str
    description: str
    ingredients: List[str]
    cooking_steps: List[str]
    video_name: Optional[str] = None
    custom_settings: Optional[Dict[str, Any]] = None

class VideoStatusResponse(BaseModel):
    job_id: str
    status: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    error_message: Optional[str] = None

# Store active video jobs
active_jobs: Dict[str, VideoGenerationResult] = {}

@app.post("/api/videos/generate")
async def generate_video_from_prompt(request: VideoGenerationRequest):
    """Generate a video from a chef's prompt using Velo 3"""
    try:
        result = await velo3_video_service.generate_video_from_chef_prompt(
            chef_prompt=request.chef_prompt,
            menu_item=request.menu_item,
            video_name=request.video_name,
            custom_settings=request.custom_settings
        )
        
        if result.status == "failed":
            raise HTTPException(status_code=500, detail=result.error_message)
        
        active_jobs[result.job_id] = result
        
        return {
            "success": True,
            "job_id": result.job_id,
            "message": "Velo 3 video generation started successfully",
            "status_url": f"/api/videos/status/{result.job_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Velo 3 video generation: {str(e)}")

@app.post("/api/videos/generate-menu-item")
async def generate_video_from_menu_item(request: MenuItemVideoRequest):
    """Generate a video from complete menu item details using Velo 3"""
    try:
        result = await velo3_video_service.generate_video_from_menu_item(
            menu_item=request.menu_item,
            description=request.description,
            ingredients=request.ingredients,
            cooking_steps=request.cooking_steps,
            video_name=request.video_name,
            custom_settings=request.custom_settings
        )
        
        if result.status == "failed":
            raise HTTPException(status_code=500, detail=result.error_message)
        
        active_jobs[result.job_id] = result
        
        return {
            "success": True,
            "job_id": result.job_id,
            "message": "Velo 3 menu item video generation started successfully",
            "status_url": f"/api/videos/status/{result.job_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Velo 3 menu item video generation: {str(e)}")

@app.get("/api/videos/status/{job_id}")
async def get_video_status(job_id: str):
    """Get the status of a Velo 3 video generation job"""
    try:
        if job_id in active_jobs:
            job = active_jobs[job_id]
            if job.status in ["pending", "processing"]:
                updated_job = await velo3_video_service.get_video_status(job_id)
                active_jobs[job_id] = updated_job
                job = updated_job
        else:
            job = await velo3_video_service.get_video_status(job_id)
            active_jobs[job_id] = job
        
        return VideoStatusResponse(
            job_id=job.job_id,
            status=job.status,
            video_url=job.video_url,
            thumbnail_url=job.thumbnail_url,
            duration=job.duration,
            error_message=job.error_message
        )
        
    except Exception as e:
        return VideoStatusResponse(
            job_id=job_id,
            status="error",
            error_message=str(e)
        )

@app.get("/api/videos/my-videos")
async def get_my_videos():
    """Get all video generation jobs"""
    return {
        "videos": [
            {
                "job_id": job.job_id,
                "status": job.status,
                "video_url": job.video_url,
                "thumbnail_url": job.thumbnail_url,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
            for job in active_jobs.values()
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CulinaAI Velo 3 Video Service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting CulinaAI Velo 3 Video Service...")
    print("This service uses Velo 3 powered by Gemini for video generation")
    uvicorn.run(app, host="0.0.0.0", port=8000)