"""
Velo 3 Video Generation Service powered by Gemini
Handles AI-powered video creation for chef prompts and menu descriptions
"""

import httpx
import asyncio
import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import os
from datetime import datetime, timedelta
GEMINI_AVAILABLE = False
genai = None

# Try to import Gemini, but make it completely optional
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except (ImportError, TypeError, Exception) as e:
    print(f"Gemini AI not available for Velo 3 (this is OK): {e}")
    GEMINI_AVAILABLE = False
    genai = None

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

class Velo3VideoService:
    """
    Service for generating videos using Velo 3 powered by Gemini
    Creates video scripts, scenes, and generates videos optimized for culinary content
    """
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.velo3_api_base = "https://api.velo3.ai/v1"
        self.access_token = None
        
        # Initialize Gemini
        if self.gemini_api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
            
        # Velo 3 video settings optimized for culinary content
        self.default_settings = {
            "resolution": "1920x1080",
            "fps": 30,
            "duration": 60,  # 60 seconds default
            "style": "cinematic",
            "mood": "elegant",
            "color_palette": "warm",
            "voice": {
                "language": "en-US",
                "gender": "neutral",
                "speed": 1.0,
                "tone": "professional"
            },
            "music": {
                "genre": "ambient",
                "tempo": "slow",
                "volume": 0.3
            }
        }
    
    def _generate_culinary_script(self, dish_name: str, description: str, ingredients: List[str], cooking_steps: List[str]) -> Dict[str, Any]:
        """Generate a professional culinary video script using Gemini"""
        if not self.gemini_model:
            print("Gemini not available, using fallback script")
            return self._create_fallback_script(dish_name, description, ingredients, cooking_steps)
            
        prompt = f"""
        Create a professional video script for a culinary dish called "{dish_name}".
        
        Dish Description: {description}
        Ingredients: {', '.join(ingredients)}
        Cooking Steps: {'; '.join(cooking_steps)}
        
        Generate a JSON response with the following structure:
        {{
            "scenes": [
                {{
                    "scene_number": 1,
                    "duration": 10,
                    "visual_description": "description of what to show",
                    "narration": "voice over text",
                    "camera_movement": "camera movement instruction",
                    "lighting": "lighting description"
                }}
            ],
            "total_duration": 60,
            "style_notes": "overall style and mood notes"
        }}
        
        Make it elegant, professional, and appetizing. Focus on the artistry of cooking.
        Each scene should be 8-15 seconds long. Include close-ups of ingredients, cooking process, and final plating.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            script_data = json.loads(response.text)
            return script_data
        except Exception as e:
            print(f"Gemini script generation failed: {e}, using fallback")
            return self._create_fallback_script(dish_name, description, ingredients, cooking_steps)
    
    def _create_fallback_script(self, dish_name: str, description: str, ingredients: List[str], cooking_steps: List[str]) -> Dict[str, Any]:
        """Create a fallback script if Gemini is not available"""
        scenes = [
            {
                "scene_number": 1,
                "duration": 12,
                "visual_description": f"Beautiful ingredients for {dish_name} arranged on a marble countertop",
                "narration": f"Welcome to the art of culinary excellence. Today, we're creating {dish_name}, {description}",
                "camera_movement": "slow pan across ingredients",
                "lighting": "soft natural lighting"
            },
            {
                "scene_number": 2,
                "duration": 15,
                "visual_description": "Chef hands preparing ingredients, chopping and seasoning",
                "narration": "Every ingredient is carefully selected and prepared with precision and passion.",
                "camera_movement": "close-up shots of preparation",
                "lighting": "bright kitchen lighting"
            },
            {
                "scene_number": 3,
                "duration": 18,
                "visual_description": "Cooking process showing techniques and transformation of ingredients",
                "narration": "Watch as simple ingredients transform into something extraordinary through skill and technique.",
                "camera_movement": "overhead and side angles",
                "lighting": "warm cooking lighting"
            },
            {
                "scene_number": 4,
                "duration": 10,
                "visual_description": f"Final plating of {dish_name} with elegant presentation",
                "narration": f"The result: {dish_name}, a perfect balance of flavors, textures, and visual appeal.",
                "camera_movement": "slow reveal from different angles",
                "lighting": "restaurant-style presentation lighting"
            }
        ]
        
        return {
            "scenes": scenes,
            "total_duration": 55,
            "style_notes": "Elegant, professional culinary presentation with warm, appetizing visuals"
        }
    
    async def _generate_video_with_velo3(self, script: Dict[str, Any], video_name: str, custom_settings: Optional[Dict[str, Any]] = None) -> str:
        """Generate video using Velo 3 API with the culinary script"""
        
        settings = self.default_settings.copy()
        if custom_settings:
            settings.update(custom_settings)
            
        # Prepare Velo 3 video request
        video_request = {
            "script": script,
            "settings": {
                "resolution": settings["resolution"],
                "fps": settings["fps"],
                "style": settings["style"],
                "mood": settings["mood"],
                "color_palette": settings["color_palette"],
                "voice": settings["voice"],
                "music": settings["music"],
                "watermark": False,
                "brand_colors": ["#00A8FF", "#14B0FF", "#19B3FF"]
            },
            "metadata": {
                "title": video_name,
                "description": f"Culinary video for {video_name}",
                "tags": ["culinary", "cooking", "food", "restaurant"]
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Start video generation
                response = await client.post(
                    f"{self.velo3_api_base}/videos/generate",
                    json=video_request,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.gemini_api_key}"
                    },
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Velo 3 API error: {response.text}")
                
                job_data = response.json()
                job_id = job_data.get("job_id") or job_data.get("id")
                
                if not job_id:
                    raise Exception("No job ID received from Velo 3")
                
                return job_id
                
        except Exception as e:
            raise Exception(f"Video generation failed: {str(e)}")
    
    async def generate_video_from_menu_item(
        self, 
        menu_item: str,
        description: str,
        ingredients: List[str],
        cooking_steps: List[str],
        custom_settings: Optional[Dict[str, Any]] = None,
        video_name: Optional[str] = None
    ) -> VideoGenerationResult:
        """
        Generate a video specifically for a menu item using Velo 3 + Gemini
        
        Args:
            menu_item: Name of the dish
            description: Dish description
            ingredients: List of ingredients
            cooking_steps: List of cooking steps
            custom_settings: Optional custom video settings
            video_name: Optional custom video name
            
        Returns:
            VideoGenerationResult with job details
        """
        try:
            # Generate culinary script using Gemini
            script = self._generate_culinary_script(menu_item, description, ingredients, cooking_steps)
            
            # Create video name if not provided
            if not video_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_item_name = menu_item.replace(" ", "_").lower()
                video_name = f"velo3_culinary_{safe_item_name}_{timestamp}"
            
            # Generate video with Velo 3
            job_id = await self._generate_video_with_velo3(script, video_name, custom_settings)
            
            return VideoGenerationResult(
                job_id=job_id,
                status="processing",
                created_at=datetime.now()
            )
            
        except Exception as e:
            return VideoGenerationResult(
                job_id="",
                status="failed",
                error_message=str(e),
                created_at=datetime.now()
            )
    
    async def generate_video_from_chef_prompt(
        self, 
        chef_prompt: str, 
        menu_item: Optional[str] = None,
        video_name: Optional[str] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> VideoGenerationResult:
        """
        Generate a video from a chef's prompt using Velo 3 + Gemini
        
        Args:
            chef_prompt: The chef's description or cooking instructions
            menu_item: Optional name of the menu item
            video_name: Optional custom video name
            custom_settings: Optional custom video settings
            
        Returns:
            VideoGenerationResult with job details
        """
        try:
            # Extract ingredients and cooking steps from the prompt using Gemini
            if self.gemini_model and GEMINI_AVAILABLE:
                extraction_prompt = f"""
                Extract ingredients and cooking steps from this chef prompt:
                "{chef_prompt}"
                
                Respond with JSON format:
                {{
                    "ingredients": ["ingredient1", "ingredient2"],
                    "cooking_steps": ["step1", "step2"],
                    "description": "brief description of the dish"
                }}
                """
                
                try:
                    response = self.gemini_model.generate_content(extraction_prompt)
                    extracted_data = json.loads(response.text)
                    ingredients = extracted_data.get("ingredients", [])
                    cooking_steps = extracted_data.get("cooking_steps", [])
                    description = extracted_data.get("description", chef_prompt)
                except:
                    # Fallback if extraction fails
                    ingredients = []
                    cooking_steps = [chef_prompt]
                    description = chef_prompt
            else:
                ingredients = []
                cooking_steps = [chef_prompt]
                description = chef_prompt
            
            # Use the main menu item function
            return await self.generate_video_from_menu_item(
                menu_item=menu_item or "Chef's Special",
                description=description,
                ingredients=ingredients,
                cooking_steps=cooking_steps,
                custom_settings=custom_settings,
                video_name=video_name
            )
            
        except Exception as e:
            return VideoGenerationResult(
                job_id="",
                status="failed",
                error_message=str(e),
                created_at=datetime.now()
            )
    
    async def get_video_status(self, job_id: str) -> VideoGenerationResult:
        """
        Check the status of a Velo 3 video generation job
        
        Args:
            job_id: The job ID to check
            
        Returns:
            VideoGenerationResult with current status
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.velo3_api_base}/videos/status/{job_id}",
                    headers={
                        "Authorization": f"Bearer {self.gemini_api_key}"
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Failed to get job status: {response.text}")
                
                status_data = response.json()
                
                result = VideoGenerationResult(
                    job_id=job_id,
                    status=status_data.get("status", "unknown"),
                    video_url=status_data.get("video_url"),
                    thumbnail_url=status_data.get("thumbnail_url"),
                    duration=status_data.get("duration"),
                    completed_at=datetime.now() if status_data.get("status") == "completed" else None
                )
                
                return result
                
        except Exception as e:
            return VideoGenerationResult(
                job_id=job_id,
                status="error",
                error_message=str(e)
            )

# Global instance for easy import
velo3_video_service = Velo3VideoService()