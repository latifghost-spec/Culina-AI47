"""
Video Generation Routes for Velo 3 powered by Gemini
Handles AI-powered video creation from chef prompts and menu items
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime

from services.velo3_video_service import velo3_video_service, VideoGenerationResult
from auth import get_current_user
from db import get_db
from sqlalchemy.orm import Session
from models import ChefDB as Chef

router = APIRouter(prefix="/api/videos", tags=["video-generation"])

class VideoGenerationRequest(BaseModel):
    """Request model for video generation"""
    chef_prompt: str
    menu_item: Optional[str] = None
    video_name: Optional[str] = None
    custom_settings: Optional[Dict[str, Any]] = None

class MenuItemVideoRequest(BaseModel):
    """Request model for menu item video generation"""
    menu_item: str
    description: str
    ingredients: List[str]
    cooking_steps: List[str]
    video_name: Optional[str] = None
    custom_settings: Optional[Dict[str, Any]] = None

class VideoStatusResponse(BaseModel):
    """Response model for video status"""
    job_id: str
    status: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class VideoGenerationResponse(BaseModel):
    """Response model for video generation"""
    success: bool
    job_id: str
    message: str
    status_url: str

# Store active video jobs (in production, use Redis or database)
active_jobs: Dict[str, VideoGenerationResult] = {}

@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video_from_prompt(
    request: VideoGenerationRequest,
    current_user: Chef = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a video from a chef's prompt or description
    
    Args:
        request: Video generation request with chef prompt
        current_user: Currently authenticated chef
        db: Database session
        
    Returns:
        Video generation response with job ID
    """
    try:
        # Generate video from chef prompt using Velo 3 + Gemini
        result = await velo3_video_service.generate_video_from_chef_prompt(
            chef_prompt=request.chef_prompt,
            menu_item=request.menu_item,
            video_name=request.video_name,
            custom_settings=request.custom_settings
        )
        
        if result.status == "failed":
            raise HTTPException(status_code=500, detail=result.error_message)
        
        # Store job for status tracking
        active_jobs[result.job_id] = result
        
        return VideoGenerationResponse(
            success=True,
            job_id=result.job_id,
            message="Video generation started successfully",
            status_url=f"/api/videos/status/{result.job_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start video generation: {str(e)}")

@router.post("/generate-menu-item", response_model=VideoGenerationResponse)
async def generate_video_from_menu_item(
    request: MenuItemVideoRequest,
    current_user: Chef = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a video from complete menu item details
    
    Args:
        request: Menu item video request with all dish details
        current_user: Currently authenticated chef
        db: Database session
        
    Returns:
        Video generation response with job ID
    """
    try:
        # Generate video from menu item details using Velo 3 + Gemini
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
        
        # Store job for status tracking
        active_jobs[result.job_id] = result
        
        return VideoGenerationResponse(
            success=True,
            job_id=result.job_id,
            message="Menu item video generation started successfully",
            status_url=f"/api/videos/status/{result.job_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start menu item video generation: {str(e)}")

@router.get("/status/{job_id}", response_model=VideoStatusResponse)
async def get_video_status(
    job_id: str,
    current_user: Chef = Depends(get_current_user)
):
    """
    Get the status of a video generation job
    
    Args:
        job_id: The job ID to check
        current_user: Currently authenticated chef
        
    Returns:
        Video status with current progress and final URL when complete
    """
    try:
        # Check if job is in active jobs
        if job_id in active_jobs:
            job = active_jobs[job_id]
            # Refresh status if still pending
            if job.status in ["pending", "processing"]:
                updated_job = await velo3_video_service.get_video_status(job_id)
                active_jobs[job_id] = updated_job
                job = updated_job
        else:
            # Check status with Velo 3 API
            job = await velo3_video_service.get_video_status(job_id)
            active_jobs[job_id] = job
        
        return VideoStatusResponse(
            job_id=job.job_id,
            status=job.status,
            video_url=job.video_url,
            thumbnail_url=job.thumbnail_url,
            duration=job.duration,
            created_at=job.created_at,
            completed_at=job.completed_at,
            error_message=job.error_message
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get video status: {str(e)}")

@router.get("/my-videos")
async def get_my_videos(
    current_user: Chef = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all video generation jobs for the current chef
    
    Args:
        current_user: Currently authenticated chef
        db: Database session
        
    Returns:
        List of video jobs belonging to the chef
    """
    try:
        # In a real implementation, store jobs in database
        # For now, return active jobs (this is simplified)
        user_jobs = []
        for job_id, job in active_jobs.items():
            user_jobs.append({
                "job_id": job.job_id,
                "status": job.status,
                "video_url": job.video_url,
                "thumbnail_url": job.thumbnail_url,
                "created_at": job.created_at,
                "completed_at": job.completed_at
            })
        
        return {"videos": user_jobs, "total": len(user_jobs)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user videos: {str(e)}")

@router.delete("/cancel/{job_id}")
async def cancel_video_job(
    job_id: str,
    current_user: Chef = Depends(get_current_user)
):
    """
    Cancel a video generation job
    
    Args:
        job_id: The job ID to cancel
        current_user: Currently authenticated chef
        
    Returns:
        Success confirmation
    """
    try:
        if job_id in active_jobs:
            del active_jobs[job_id]
            return {"success": True, "message": "Video job cancelled successfully"}
        else:
            raise HTTPException(status_code=404, detail="Video job not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel video job: {str(e)}")

@router.get("/templates")
async def get_video_templates():
    """
    Get available video templates and settings for chefs
    
    Returns:
        Available video templates and customization options
    """
    return {
        "templates": [
            {
                "id": "culinary_storytelling",
                "name": "Culinary Storytelling",
                "description": "Professional storytelling format for menu items and chef experiences",
                "settings": {
                    "voice_over": {"speaker": "Brian", "speed": 100},
                    "background_music": {"volume": 0.3, "auto_music": True}
                }
            },
            {
                "id": "recipe_tutorial",
                "name": "Recipe Tutorial",
                "description": "Step-by-step cooking instructions with clear narration",
                "settings": {
                    "voice_over": {"speaker": "Aditi", "speed": 95},
                    "background_music": {"volume": 0.2, "auto_music": True}
                }
            },
            {
                "id": "restaurant_promo",
                "name": "Restaurant Promotion",
                "description": "Engaging promotional content for restaurants and dishes",
                "settings": {
                    "voice_over": {"speaker": "Matthew", "speed": 105},
                    "background_music": {"volume": 0.4, "auto_music": True}
                }
            }
        ],
        "ai_voices": [
            {"id": "Brian", "name": "Brian", "description": "Professional, warm male voice"},
            {"id": "Aditi", "name": "Aditi", "description": "Friendly, clear female voice"},
            {"id": "Matthew", "name": "Matthew", "description": "Energetic, engaging male voice"},
            {"id": "Joanna", "name": "Joanna", "description": "Sophisticated, elegant female voice"}
        ],
        "video_formats": [
            {"width": 1920, "height": 1080, "name": "Full HD (16:9)"},
            {"width": 1080, "height": 1080, "name": "Square (1:1)"},
            {"width": 1080, "height": 1920, "name": "Vertical (9:16)"}
        ]
    }