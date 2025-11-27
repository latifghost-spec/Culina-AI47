"""
Video Generation Service using Pictory API
Handles text-to-video conversion for chef prompts and menu descriptions
"""

import httpx
import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import os
from datetime import datetime, timedelta

@dataclass
class VideoGenerationResult:
    """Result of video generation process"""
    job_id: str
    video_url: Optional[str] = None
    status: str = "pending"
    error_message: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None
    thumbnail_url: Optional[str] = None

class VideoGenerationService:
    """
    Service for generating videos from text using Pictory API
    Optimized for chef prompts and culinary content
    """
    
    def __init__(self):
        self.api_base_url = "https://api.pictory.ai/pictoryapis"
        self.client_id = os.getenv("PICTORY_CLIENT_ID", "")
        self.client_secret = os.getenv("PICTORY_CLIENT_SECRET", "")
        self.access_token = None
        self.token_expires_at = None
        
        # Culinary-focused video settings
        self.default_settings = {
            "video_width": 1920,
            "video_height": 1080,
            "language": "en",
            "background_music": {
                "enabled": True,
                "auto_music": True,
                "volume": 0.3
            },
            "voice_over": {
                "enabled": True,
                "ai_voices": [
                    {
                        "speaker": "Brian",  # Professional, warm voice
                        "speed": 100,
                        "amplify_level": 0
                    }
                ]
            }
        }
        
        # Culinary-specific visual keywords for better scene generation
        self.culinary_keywords = [
            "cooking", "kitchen", "chef", "restaurant", "food preparation",
            "ingredients", "culinary", "gourmet", "cuisine", "recipe",
            "plating", "presentation", "farm to table", "fresh ingredients",
            "cooking techniques", "culinary artistry", "dining experience"
        ]
    
    async def _get_access_token(self) -> str:
        """Get or refresh access token"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Pictory API credentials not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base_url}/v1/oauth2/token",
                json={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get access token: {response.text}")
            
            data = response.json()
            self.access_token = data["access_token"]
            # Set token expiry with 5-minute buffer
            self.token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"] - 300)
            
            return self.access_token
    
    def _enhance_chef_prompt(self, chef_prompt: str, menu_item: Optional[str] = None) -> str:
        """
        Enhance chef prompts with culinary-specific language and structure
        for better video generation results
        """
        enhanced_prompt = chef_prompt
        
        # Add culinary context if menu item is provided
        if menu_item:
            enhanced_prompt = f"{menu_item}: {chef_prompt}"
        
        # Add culinary storytelling elements
        if not any(keyword in enhanced_prompt.lower() for keyword in ["experience", "journey", "story"]):
            enhanced_prompt += " Discover the culinary journey behind this exquisite dish."
        
        # Add sensory details if missing
        if not any(word in enhanced_prompt.lower() for word in ["aroma", "texture", "flavor", "taste", "visual"]):
            enhanced_prompt += " Experience the perfect harmony of flavors, textures, and visual presentation."
        
        # Add cooking process elements if missing
        if not any(word in enhanced_prompt.lower() for word in ["preparation", "cooking", "technique", "method"]):
            enhanced_prompt += " Learn the professional techniques and careful preparation that make this dish special."
        
        return enhanced_prompt
    
    def _create_culinary_scenes(self, text: str, menu_item: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Create structured scenes optimized for culinary content
        """
        # Split text into logical scenes
        sentences = text.split('.')
        scenes = []
        
        # First scene: Introduction/Hook
        intro_text = f"Welcome to the culinary world of {menu_item or 'gourmet cuisine'}" if menu_item else "Welcome to the culinary arts"
        scenes.append({
            "story": intro_text,
            "createSceneOnNewLine": True,
            "createSceneOnEndOfSentence": True
        })
        
        # Main content scenes
        current_scene = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Skip very short sentences
                current_scene += sentence + ". "
                if len(current_scene) > 150:  # Create new scene when text is long enough
                    scenes.append({
                        "story": current_scene.strip(),
                        "createSceneOnNewLine": False,
                        "createSceneOnEndOfSentence": True
                    })
                    current_scene = ""
        
        # Add remaining text as final scene
        if current_scene.strip():
            scenes.append({
                "story": current_scene.strip(),
                "createSceneOnNewLine": False,
                "createSceneOnEndOfSentence": True
            })
        
        # Final scene: Call to action
        if menu_item:
            cta_text = f"Experience {menu_item} and discover the art of fine dining."
        else:
            cta_text = "Experience the art of culinary excellence and create memorable dining moments."
        
        scenes.append({
            "story": cta_text,
            "createSceneOnNewLine": True,
            "createSceneOnEndOfSentence": True
        })
        
        return scenes
    
    async def generate_video_from_chef_prompt(
        self, 
        chef_prompt: str, 
        menu_item: Optional[str] = None,
        video_name: Optional[str] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> VideoGenerationResult:
        """
        Generate a video from a chef's prompt or menu description
        
        Args:
            chef_prompt: The chef's description or cooking instructions
            menu_item: Optional name of the menu item
            video_name: Optional custom video name
            custom_settings: Optional custom video settings
            
        Returns:
            VideoGenerationResult with job details and final video URL
        """
        try:
            # Get access token
            token = await self._get_access_token()
            
            # Enhance the prompt for culinary content
            enhanced_prompt = self._enhance_chef_prompt(chef_prompt, menu_item)
            
            # Create structured scenes
            scenes = self._create_culinary_scenes(enhanced_prompt, menu_item)
            
            # Prepare video settings
            video_settings = self.default_settings.copy()
            if custom_settings:
                video_settings.update(custom_settings)
            
            # Set video name
            if not video_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                video_name = f"culinary_video_{timestamp}"
                if menu_item:
                    safe_item_name = menu_item.replace(" ", "_").lower()
                    video_name = f"culinary_{safe_item_name}_{timestamp}"
            
            # Create video request
            video_request = {
                "videoName": video_name,
                "videoWidth": video_settings["video_width"],
                "videoHeight": video_settings["video_height"],
                "language": video_settings["language"],
                "backgroundMusic": video_settings["background_music"],
                "voiceOver": video_settings["voice_over"],
                "scenes": scenes
            }
            
            # Start video generation
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/v2/video/storyboard/render",
                    json=video_request,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": token
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Failed to create video: {response.text}")
                
                job_data = response.json()
                job_id = job_data["data"]["jobId"]
                
                result = VideoGenerationResult(
                    job_id=job_id,
                    created_at=datetime.now()
                )
                
                return result
                
        except Exception as e:
            return VideoGenerationResult(
                job_id="",
                status="failed",
                error_message=str(e),
                created_at=datetime.now()
            )
    
    async def get_video_status(self, job_id: str) -> VideoGenerationResult:
        """
        Check the status of a video generation job
        
        Args:
            job_id: The job ID to check
            
        Returns:
            VideoGenerationResult with current status
        """
        try:
            token = await self._get_access_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/v1/jobs/{job_id}",
                    headers={"Authorization": token}
                )
                
                if response.status_code != 200:
                    raise Exception(f"Failed to get job status: {response.text}")
                
                job_data = response.json()["data"]
                
                result = VideoGenerationResult(
                    job_id=job_id,
                    status=job_data.get("status", "unknown"),
                    video_url=job_data.get("videoURL"),
                    thumbnail_url=job_data.get("thumbnailURL"),
                    duration=job_data.get("duration"),
                    completed_at=datetime.now() if job_data.get("status") == "completed" else None
                )
                
                return result
                
        except Exception as e:
            return VideoGenerationResult(
                job_id=job_id,
                status="error",
                error_message=str(e)
            )
    
    async def generate_video_from_menu_item(
        self, 
        menu_item: str,
        description: str,
        ingredients: List[str],
        cooking_steps: List[str],
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> VideoGenerationResult:
        """
        Generate a video specifically for a menu item with all details
        
        Args:
            menu_item: Name of the dish
            description: Dish description
            ingredients: List of ingredients
            cooking_steps: List of cooking steps
            custom_settings: Optional custom video settings
            
        Returns:
            VideoGenerationResult with job details
        """
        # Create comprehensive prompt from menu details
        prompt = f"""
        {menu_item}: {description}
        
        Ingredients: {', '.join(ingredients)}
        
        Cooking Process:
        {' '.join([f"Step {i+1}: {step}" for i, step in enumerate(cooking_steps)])}
        
        This dish represents the perfect balance of flavors and textures, created with passion and culinary expertise.
        """
        
        return await self.generate_video_from_chef_prompt(
            chef_prompt=prompt,
            menu_item=menu_item,
            custom_settings=custom_settings
        )

# Global instance for easy import
video_service = VideoGenerationService()