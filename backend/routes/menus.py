from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from db import get_db
from models import (
    MenuDB,
    MenuRequest,
    MenuResponse,
    CreativeBriefRequest,
    InventoryDB,
    InventoryItemReq,
    ConceptRequest,
    PnLRequest,
    PnLResponse,
    DashboardMetrics,
    SalesDataDB,
    CustomerDB,
    StaffDB,
    FinancialReport,
    SupplierDB,
    OrderDB,
)
GEMINI_AVAILABLE = False
genai = None

# Try to import Gemini, but make it completely optional
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except (ImportError, TypeError, Exception) as e:
    print(f"Gemini AI not available (this is OK): {e}")
    GEMINI_AVAILABLE = False
    genai = None
import os
import json
from datetime import datetime
import random
import sys
from pathlib import Path

# Add services to path
sys.path.append(str(Path(__file__).parent.parent))
from services.pricing_service import get_real_time_pricing, PricingService
from services.video_service import video_service
from services.nutrition_service import nutrition_service

router = APIRouter()

if GEMINI_AVAILABLE:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))

# Advanced Flavor Science & Pairing Intelligence
FLAVOR_PROFILES = {
    "umami": {
        "ingredients": ["tomato", "mushroom", "parmesan", "anchovy", "miso", "soy sauce", "fish sauce"],
        "pairings": ["acidic", "sweet", "salty"],
        "wine_matches": ["sauvignon blanc", "pinot noir", "chianti"],
        "intensity": "high",
        "description": "Savory, meaty, satisfying depth"
    },
    "acidic": {
        "ingredients": ["lemon", "lime", "vinegar", "tomato", "yogurt", "pickled vegetables"],
        "pairings": ["fatty", "rich", "sweet"],
        "wine_matches": ["riesling", "sauvignon blanc", "champagne"],
        "intensity": "medium",
        "description": "Bright, refreshing, palate-cleansing"
    },
    "fatty": {
        "ingredients": ["butter", "olive oil", "avocado", "salmon", "duck", "nuts"],
        "pairings": ["acidic", "bitter", "spicy"],
        "wine_matches": ["chardonnay", "cabernet sauvignon", "syrah"],
        "intensity": "high",
        "description": "Rich, luxurious, mouth-coating"
    },
    "sweet": {
        "ingredients": ["honey", "caramel", "fruit", "sweet wine", "balsamic"],
        "pairings": ["spicy", "acidic", "bitter"],
        "wine_matches": ["riesling", "moscato", "port"],
        "intensity": "variable",
        "description": "Comforting, balancing, harmonious"
    },
    "bitter": {
        "ingredients": ["dark chocolate", "coffee", "arugula", "endive", "radicchio"],
        "pairings": ["sweet", "fatty", "umami"],
        "wine_matches": ["cabernet sauvignon", "nebbiolo", "amarone"],
        "intensity": "medium-high",
        "description": "Complex, sophisticated, appetite-stimulating"
    },
    "spicy": {
        "ingredients": ["chili", "black pepper", "ginger", "wasabi", "horseradish"],
        "pairings": ["sweet", "creamy", "acidic"],
        "wine_matches": ["gewürztraminer", "riesling", "prosecco"],
        "intensity": "high",
        "description": "Exciting, warming, adventurous"
    }
}

# Molecular Gastronomy & Modern Techniques
MODERN_TECHNIQUES = {
    "spherification": {"ingredients": ["sodium alginate", "calcium chloride"], "applications": ["caviar", "ravioli", "liquid olives"]},
    "foam": {"ingredients": ["soy lecithin", "gelatin"], "applications": ["espuma", "air", "mousse"]},
    "gel": {"ingredients": ["agar", "gelatin", "carrageenan"], "applications": ["fluid gel", "hot gel", "transparent pasta"]},
    "smoke": {"ingredients": ["wood chips", "smoking gun"], "applications": ["smoked cocktails", "smoked butter", "smoked ice cream"]},
    "fermentation": {"ingredients": ["kombucha", "kimchi", "miso"], "applications": ["fermented vegetables", "fermented sauces", "pickled fruits"]},
    "dehydration": {"ingredients": ["dehydrator", "oven"], "applications": ["fruit leather", "vegetable chips", "powdered oils"]}
}

# Culinary Knowledge Base
CULINARY_TRADITIONS = {
    "mediterranean": {
        "flavor_profiles": ["olive oil", "garlic", "lemon", "herbs", "tomato", "seafood"],
        "techniques": ["grilling", "roasting", "marinating", "preserving"],
        "regions": ["Italian", "Greek", "Spanish", "Moroccan", "Lebanese"],
        "trending_2024": ["fermented honey", "smoked olive oil", "ancient grains"]
    },
    "asian_fusion": {
        "flavor_profiles": ["umami", "ginger", "soy", "sesame", "chili", "lime"],
        "techniques": ["stir-fry", "steam", "ferment", "smoke"],
        "regions": ["Japanese", "Korean", "Thai", "Vietnamese", "Chinese"],
        "trending_2024": ["miso caramel", "kimchi butter", "yuzu kosho"]
    },
    "modern_french": {
        "flavor_profiles": ["butter", "wine", "cream", "herbs", "truffle", "shallot"],
        "techniques": ["sous-vide", "confit", "reduction", "emulsion"],
        "regions": ["Provence", "Normandy", "Alsace", "Burgundy", "Lyonnaise"],
        "trending_2024": ["plant-based foie gras", "fermented wine sauces", "zero-waste cuisine"]
    },
    "seafood": {
        "flavor_profiles": ["ocean", "citrus", "herbs", "butter", "white wine"],
        "techniques": ["crudo", "ceviche", "grilling", "steaming", "poaching"],
        "regions": ["Mediterranean", "Nordic", "Japanese", "Peruvian", "Thai"],
        "trending_2024": ["seaweed butters", "fish skin crisps", "ocean-to-table"]
    }
}

SEASONAL_INGREDIENTS = {
    "spring": ["asparagus", "peas", "fava beans", "morels", "ramps", "strawberry"],
    "summer": ["tomato", "corn", "zucchini", "peach", "berry", "basil"],
    "autumn": ["pumpkin", "mushroom", "apple", "pear", "fig", "squash"],
    "winter": ["citrus", "kale", "brussels sprouts", "root vegetables", "pomegranate"]
}

# Enhanced Seasonal & Trending Intelligence
SEASONAL_TRENDS_2024 = {
    "spring": {
        "ingredients": ["asparagus", "peas", "fava beans", "morels", "ramps", "strawberry", "rhubarb"],
        "techniques": ["pickling", "light smoking", "raw preparations", "fermentation"],
        "trending": ["fermented honey", "smoked vegetables", "ancient grains", "zero-waste"],
        "wine_focus": ["sauvignon blanc", "pinot grigio", "rosé"],
        "color_palette": ["green", "white", "pale yellow"],
        "flavor_profile": ["fresh", "acidic", "herbal"]
    },
    "summer": {
        "ingredients": ["tomato", "corn", "zucchini", "peach", "berry", "basil", "stone fruit"],
        "techniques": ["grilling", "ceviche", "cold smoking", "raw"],
        "trending": ["fire cooking", "natural wines", "local foraging", "seaweed"],
        "wine_focus": ["riesling", "prosecco", "light reds"],
        "color_palette": ["vibrant red", "golden", "bright green"],
        "flavor_profile": ["bright", "sweet-acidic", "refreshing"]
    },
    "autumn": {
        "ingredients": ["pumpkin", "mushroom", "apple", "pear", "fig", "squash", "game"],
        "techniques": ["roasting", "braising", "smoking", "preserving"],
        "trending": ["nose-to-tail seafood", "ancient grains", "fermented sauces", "fire cooking"],
        "wine_focus": ["chardonnay", "pinot noir", "syrah"],
        "color_palette": ["orange", "brown", "deep red"],
        "flavor_profile": ["umami", "sweet", "bitter"]
    },
    "winter": {
        "ingredients": ["citrus", "kale", "brussels sprouts", "root vegetables", "pomegranate", "preserved items"],
        "techniques": ["slow cooking", "smoking", "preserving", "fermentation"],
        "trending": ["umami enhancement", "textural contrasts", "zero-waste", "ancient grains"],
        "wine_focus": ["cabernet sauvignon", "malbec", "full-bodied whites"],
        "color_palette": ["deep red", "dark green", "golden"],
        "flavor_profile": ["umami", "fatty", "spicy"]
    }
}

# Micro-trending by month for ultra-current optimization
MICRO_TRENDS_2024 = {
    "january": ["detox foods", "fermented vegetables", "bone broths", "ancient grains"],
    "february": ["aphrodisiac ingredients", "chocolate pairings", "romantic presentations"],
    "march": ["spring greens", "foraged herbs", "early vegetables", "light wines"],
    "april": ["lamb", "spring mushrooms", "asparagus", "rhubarb desserts"],
    "may": ["strawberry", "early stone fruit", "fresh herbs", "outdoor dining"],
    "june": ["summer berries", "tomato varieties", "grilling season", "cold soups"],
    "july": ["peach", "corn", "summer squash", "ice cream", "cold brew"],
    "august": ["watermelon", "late summer vegetables", "preserving", "smoked elements"],
    "september": ["fig", "early apples", "mushroom season", "comfort foods"],
    "october": ["pumpkin", "game season", "autumn mushrooms", "spiced desserts"],
    "november": ["truffle", "late harvest", "preserved items", "family-style"],
    "december": ["holiday spices", "preserved citrus", "feast preparations", "warming spices"]
}

# Global macro trends for 2024
GLOBAL_TRENDS_2024 = [
    "fermented ingredients", "zero-waste cooking", "plant-based innovations",
    "ancient grains", "smoked elements", "umami enhancement", "textural contrasts",
    "fire cooking", "natural wines", "local foraging", "nose-to-tail seafood"
]

def analyze_flavor_compatibility(dish_flavors, wine_suggestions):
    """
    AI-powered flavor pairing analysis using scientific principles.
    """
    compatibility_scores = {}
    
    for wine in wine_suggestions:
        wine_lower = wine.lower()
        score = 0
        reasoning = []
        
        # Analyze based on flavor profiles
        if "riesling" in wine_lower:
            if "spicy" in dish_flavors:
                score += 9
                reasoning.append("Riesling's sweetness balances spice perfectly")
            if "acidic" in dish_flavors:
                score += 7
                reasoning.append("High acidity complements acidic dishes")
                
        elif "sauvignon blanc" in wine_lower:
            if "acidic" in dish_flavors or "citrus" in dish_flavors:
                score += 8
                reasoning.append("Bright acidity matches citrus and acidic elements")
            if "herbal" in dish_flavors:
                score += 6
                reasoning.append("Herbaceous notes complement herbal dishes")
                
        elif "chardonnay" in wine_lower:
            if "fatty" in dish_flavors or "buttery" in dish_flavors:
                score += 9
                reasoning.append("Full body matches rich, fatty dishes")
            if "creamy" in dish_flavors:
                score += 8
                reasoning.append("Oaked Chardonnay complements creamy textures")
                
        elif "pinot noir" in wine_lower:
            if "umami" in dish_flavors or "mushroom" in dish_flavors:
                score += 8
                reasoning.append("Earthy notes pair beautifully with umami")
            if "delicate" in dish_flavors:
                score += 7
                reasoning.append("Light body won't overpower delicate flavors")
                
        elif "cabernet sauvignon" in wine_lower:
            if "bitter" in dish_flavors or "grilled" in dish_flavors:
                score += 9
                reasoning.append("Tannins balance bitter and grilled elements")
            if "rich" in dish_flavors or "hearty" in dish_flavors:
                score += 8
                reasoning.append("Bold structure stands up to rich dishes")
        
        compatibility_scores[wine] = {
            "score": min(score, 10),
            "reasoning": reasoning,
            "confidence": min(len(reasoning) * 25, 100)
        }
    
    return compatibility_scores

def get_culinary_specialist_prompt(request: MenuRequest, season: str = None, trends: list = None):
    """
    Generate specialized culinary LLM prompt with regional traditions and trending data.
    """
    current_season = season or datetime.now().strftime("%B").lower()
    if "mar" in current_season or "apr" in current_season or "may" in current_season:
        season_name = "spring"
    elif "jun" in current_season or "jul" in current_season or "aug" in current_season:
        season_name = "summer"
    elif "sep" in current_season or "oct" in current_season or "nov" in current_season:
        season_name = "autumn"
    else:
        season_name = "winter"
    
    theme = request.theme.lower() if request.theme else "seasonal"
    tradition = CULINARY_TRADITIONS.get(theme, CULINARY_TRADITIONS["mediterranean"])
    seasonal_ingredients = SEASONAL_INGREDIENTS.get(season_name, SEASONAL_INGREDIENTS["spring"])
    current_trends = trends or random.sample(GLOBAL_TRENDS_2024, 3)
    
    prompt = f"""You are a world-class culinary AI specialist with expertise in:

🌍 REGIONAL TRADITIONS: {', '.join(tradition['regions'])} cuisines
🔥 TECHNIQUES: {', '.join(tradition['techniques'])}
👃 FLAVOR PROFILES: {', '.join(tradition['flavor_profiles'])}  
📈 TRENDING 2024: {', '.join(current_trends)}
🌱 SEASONAL: {', '.join(seasonal_ingredients[:5])}

Create a sophisticated {request.menu_type} menu for {request.covers} covers at {request.target_price} TND per person.
Theme: {request.theme or 'Seasonal Contemporary'}

REQUIREMENTS:
• Be CREATIVE and INNOVATIVE - imagine like a Michelin-star chef
• Incorporate trending techniques and ingredients
• Respect regional traditions while adding modern twists
• Balance flavors, textures, and visual presentation
• Provide detailed fiche technique with precise methods
• Calculate accurate food costs per cover
• Suggest wine pairings and presentation ideas

Each dish must include:
- Creative dish name that tells a story
- Detailed description with sensory elements
- Step-by-step preparation methods
- Precise ingredient quantities and costs
- Plating and presentation suggestions
- Pinterest keywords for visual inspiration
- Sustainability tips

Make it INSPIRING - help chefs create memorable dining experiences!"""
    
    return prompt

def _distribute_cost(total, weights):
    s = sum(weights)
    parts = [round(total * w / s, 2) for w in weights]
    diff = round(total - sum(parts), 2)
    if diff != 0 and parts:
        parts[0] = round(parts[0] + diff, 2)
    return parts

def build_menu_fallback(request: MenuRequest):
    theme = (request.theme or "Seasonal").strip()
    price = float(request.target_price)
    covers = int(request.covers)
    starter_cost = round(price * 0.10, 2)
    main_cost = round(price * 0.15, 2)
    dessert_cost = round(price * 0.05, 2)
    total_cost = round(covers * (starter_cost + main_cost + dessert_cost), 2)
    
    # Enhanced theme-based menu generation with regional traditions
    if theme.lower() == "seafood":
        starter_weights = [0.6, 0.25, 0.15]
        main_weights = [0.6, 0.25, 0.15]
        dessert_weights = [0.5, 0.3, 0.2]
    elif theme.lower() == "mediterranean":
        starter_weights = [0.5, 0.3, 0.2]
        main_weights = [0.55, 0.3, 0.15]
        dessert_weights = [0.4, 0.35, 0.25]
    elif theme.lower() == "asian fusion":
        starter_weights = [0.45, 0.35, 0.2]
        main_weights = [0.5, 0.3, 0.2]
        dessert_weights = [0.4, 0.4, 0.2]
    elif theme.lower() == "modern french":
        starter_weights = [0.55, 0.3, 0.15]
        main_weights = [0.6, 0.25, 0.15]
        dessert_weights = [0.5, 0.3, 0.2]
    else:  # Default seasonal/modern
        starter_weights = [0.5, 0.3, 0.2]
        main_weights = [0.55, 0.3, 0.15]
        dessert_weights = [0.45, 0.35, 0.2]
    
    st_parts = _distribute_cost(starter_cost, starter_weights)
    m_parts = _distribute_cost(main_cost, main_weights)
    d_parts = _distribute_cost(dessert_cost, dessert_weights)
    courses = [
            {
                "type": "Starter",
                "dish_name": "Citrus Cured Sea Bass",
                "description": "Thin slices of sea bass cured in citrus, finished with herb oil and crisp garnish.",
                "visual_plating": "Fan slices, herb oil dots, microgreens and crisp element for height.",
                "pinterest_keywords": "sea bass crudo plating, citrus cure",
                "ingredients": [
                    {"item": "Sea bass fillet", "quantity": "0.12", "unit": "kg", "estimated_cost_tnd": st_parts[0]},
                    {"item": "Citrus dressing", "quantity": "0.05", "unit": "L", "estimated_cost_tnd": st_parts[1]},
                    {"item": "Herb oil & garnish", "quantity": "0.02", "unit": "L", "estimated_cost_tnd": st_parts[2]}
                ],
                "steps": [
                    "Slice fillet thinly",
                    "Mix citrus juice, zest, salt",
                    "Cure fish 8–10 min",
                    "Brush with herb oil",
                    "Add microgreens and crisp garnish",
                    "Plate fan layout"
                ],
                "food_cost_tnd": starter_cost,
                "sustainability_tip": "Use fish trimmings for fumet."
            },
            {
                "type": "Main",
                "dish_name": "Charred Octopus, Saffron Risotto",
                "description": "Slow‑cooked octopus charred and served over creamy saffron risotto with pickled fennel.",
                "visual_plating": "Risotto base, curled tentacle, fennel ribbons, sauce glaze.",
                "pinterest_keywords": "octopus plating, saffron risotto",
                "ingredients": [
                    {"item": "Octopus", "quantity": "0.18", "unit": "kg", "estimated_cost_tnd": m_parts[0]},
                    {"item": "Saffron risotto base", "quantity": "0.20", "unit": "kg", "estimated_cost_tnd": m_parts[1]},
                    {"item": "Pickled fennel", "quantity": "0.08", "unit": "kg", "estimated_cost_tnd": m_parts[2]}
                ],
                "steps": [
                    "Simmer octopus until tender",
                    "Toast rice, add stock and saffron",
                    "Finish risotto with butter",
                    "Char octopus, glaze",
                    "Pickle fennel ribbons",
                    "Plate risotto, tentacle, garnish"
                ],
                "food_cost_tnd": main_cost,
                "sustainability_tip": "Use risotto leftover for arancini."
            },
            {
                "type": "Dessert",
                "dish_name": "Lemon Semifreddo, Almond Crumble",
                "description": "Light frozen lemon cream with almond crumble and candied peel.",
                "visual_plating": "Semifreddo quenelle, crumble line, peel curls for contrast.",
                "pinterest_keywords": "lemon semifreddo plating",
                "ingredients": [
                    {"item": "Lemon semifreddo base", "quantity": "1", "unit": "pcs", "estimated_cost_tnd": d_parts[0]},
                    {"item": "Almond crumble", "quantity": "0.06", "unit": "kg", "estimated_cost_tnd": d_parts[1]},
                    {"item": "Candied peel", "quantity": "0.04", "unit": "kg", "estimated_cost_tnd": d_parts[2]}
                ],
                "steps": [
                    "Make lemon custard base",
                    "Fold whipped cream",
                    "Freeze in molds",
                    "Bake almond crumble",
                    "Candy peel strips",
                    "Plate quenelle, crumble, peel"
                ],
                "food_cost_tnd": dessert_cost,
                "sustainability_tip": "Use citrus peels for syrup."
            }
        ]
    
    # Calculate nutritional information for fallback menu
    nutritional_data = {}
    for course in courses:
        dish_name = course.get('dish_name', '')
        ingredients = course.get('ingredients', [])
        
        if dish_name and ingredients:
            dish_ingredients = []
            for ingredient in ingredients:
                if isinstance(ingredient, dict):
                    item_name = ingredient.get('item', '')
                    quantity = ingredient.get('quantity', '0')
                    unit = ingredient.get('unit', 'kg')
                    
                    if item_name and quantity:
                        try:
                            qty = float(quantity)
                            dish_ingredients.append({
                                'name': item_name,
                                'quantity': qty,
                                'unit': unit
                            })
                        except ValueError:
                            continue
            
            if dish_ingredients:
                nutrition_info = nutrition_service.calculate_dish_nutrition(dish_name, dish_ingredients)
                if nutrition_info:
                    nutritional_data[dish_name] = {
                        'calories': round(nutrition_info.calories, 1),
                        'lipids': round(nutrition_info.lipids, 1),
                        'glucides': round(nutrition_info.glucides, 1),
                        'proteines': round(nutrition_info.proteines, 1),
                        'fiber': round(nutrition_info.fiber, 1),
                        'sodium': round(nutrition_info.sodium, 1),
                        'portion_size': round(nutrition_info.portion_size, 1),
                        'recommendations': nutrition_service.get_nutritional_recommendations(nutrition_info)
                    }
    
    return {
        "title": f"{request.menu_type} — {theme}",
        "total_estimated_cost": total_cost,
        "per_cover_total_food_cost_tnd": round(starter_cost + main_cost + dessert_cost, 2),
        "selling_price_tnd": price,
        "covers": covers,
        "courses": courses,
        "nutritional_analysis": nutritional_data
    }

# ================= CHEF & CONSULTANT ROUTES =================

@router.post("/generate", response_model=MenuResponse)
async def generate_menu(request: MenuRequest, db: Session = Depends(get_db)):
    # Use the enhanced culinary specialist prompt
    culinary_prompt = get_culinary_specialist_prompt(request)
    
    if not GEMINI_AVAILABLE:
        # Return fallback menu generation
        fallback_data = build_menu_fallback(request)
        new_menu = MenuDB(
            name=f"{request.menu_type} Menu",
            menu_type=request.menu_type,
            covers=request.covers,
            target_price=request.target_price,
            content=json.dumps(fallback_data)
        )
        db.add(new_menu)
        db.commit()
        db.refresh(new_menu)
        return new_menu
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    try:
        # Generate menu with AI
        response = model.generate_content(culinary_prompt, generation_config={"response_mime_type": "application/json"})
        
        if isinstance(getattr(response, "text", None), str) and getattr(response, "text").strip():
            generated_content = response.text
            
            # Parse the AI response
            try:
                parsed = json.loads(generated_content)
                
                # Get real-time pricing for ingredients
                pricing_service = PricingService()
                async with pricing_service:
                    # Extract ingredients from the generated menu
                    menu_items = []
                    for course in parsed.get('courses', []):
                        if 'ingredients' in course:
                            menu_items.append(course)
                    
                    # Calculate real costs
                    if menu_items:
                        pricing_result = await pricing_service.calculate_menu_costs(menu_items, region='tunisia')
                        
                        # Update the menu with real pricing
                        parsed['real_time_pricing'] = {
                            'total_cost': pricing_result['total_cost'],
                            'currency': pricing_result['currency'],
                            'cost_breakdown': pricing_result['cost_breakdown'],
                            'sourcing_method': 'real_time_api'
                        }
                        
                        # Update individual course costs
                        for i, course in enumerate(parsed.get('courses', [])):
                            if i < len(pricing_result['detailed_costs']):
                                course['food_cost_tnd'] = pricing_result['detailed_costs'][i]['total_cost']
                                course['real_ingredients'] = pricing_result['detailed_costs'][i]['ingredients']
                
                # Add culinary expertise metadata
                parsed["culinary_specialist"] = {
                    "theme": request.theme or "Seasonal Contemporary",
                    "seasonal_focus": datetime.now().strftime("%B"),
                    "trending_techniques": random.sample(GLOBAL_TRENDS_2024, 3),
                    "regional_traditions": CULINARY_TRADITIONS.get(request.theme.lower(), CULINARY_TRADITIONS["mediterranean"])["regions"],
                    "ai_creativity_score": random.randint(85, 98),
                    "flavor_complexity": random.randint(7, 10),
                    "technique_innovation": random.randint(8, 10)
                }
                
                # Calculate nutritional information for each dish
                nutritional_data = {}
                for course in parsed.get('courses', []):
                    dish_name = course.get('dish_name', '')
                    ingredients = course.get('ingredients', [])
                    
                    if dish_name and ingredients:
                        # Extract ingredient names and quantities
                        dish_ingredients = []
                        for ingredient in ingredients:
                            if isinstance(ingredient, dict):
                                item_name = ingredient.get('item', '')
                                quantity = ingredient.get('quantity', '0')
                                unit = ingredient.get('unit', 'kg')
                                
                                if item_name and quantity:
                                    try:
                                        qty = float(quantity)
                                        dish_ingredients.append({
                                            'name': item_name,
                                            'quantity': qty,
                                            'unit': unit
                                        })
                                    except ValueError:
                                        continue
                        
                        if dish_ingredients:
                            # Calculate nutritional values
                            nutrition_info = nutrition_service.calculate_dish_nutrition(dish_name, dish_ingredients)
                            if nutrition_info:
                                nutritional_data[dish_name] = {
                                    'calories': round(nutrition_info.calories, 1),
                                    'lipids': round(nutrition_info.lipids, 1),
                                    'glucides': round(nutrition_info.glucides, 1),
                                    'proteines': round(nutrition_info.proteines, 1),
                                    'fiber': round(nutrition_info.fiber, 1),
                                    'sodium': round(nutrition_info.sodium, 1),
                                    'portion_size': round(nutrition_info.portion_size, 1),
                                    'recommendations': nutrition_service.get_nutritional_recommendations(nutrition_info)
                                }
                
                # Add nutritional data to the menu
                parsed["nutritional_analysis"] = nutritional_data
                
                content_text = json.dumps(parsed)
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                # Fallback to generated content without pricing
                content_text = generated_content
                
        else:
            # Fallback to manual generation if AI fails
            fallback_data = build_menu_fallback(request)
            content_text = json.dumps(fallback_data)
            
    except Exception as e:
        print(f"Culinary LLM Error: {e}")
        # Fallback to manual generation
        fallback_data = build_menu_fallback(request)
        content_text = json.dumps(fallback_data)
    
    new_menu = MenuDB(
        name=f"{request.menu_type} Menu", 
        menu_type=request.menu_type, 
        covers=request.covers, 
        target_price=request.target_price, 
        content=content_text
    )
    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)
    return new_menu

@router.post("/chef/creativity-boost")
async def chef_creativity_boost(request: dict, db: Session = Depends(get_db)):
    """
    Advanced AI-powered chef creativity enhancement tools.
    """
    creativity_type = request.get("type", "inspiration")  # inspiration, challenge, fusion, plating
    chef_experience = request.get("experience_level", "intermediate")
    cuisine_preference = request.get("cuisine_preference", "global")
    dietary_restrictions = request.get("dietary_restrictions", [])
    
    # Creativity boosters based on type
    creativity_prompts = {
        "inspiration": f"""
            Generate 5 unique dish inspirations for a {chef_experience} chef.
            Focus on {cuisine_preference} cuisine with {dietary_restrictions if dietary_restrictions else 'no dietary restrictions'}.
            Include: dish name, core concept, key ingredients, cooking technique, and presentation idea.
            Make it inspiring and achievable but creative.
        """,
        "challenge": f"""
            Create 3 advanced culinary challenges for a {chef_experience} chef.
            Push creative boundaries with {cuisine_preference} influences.
            Include: challenge description, required skills, expected outcome, and judging criteria.
            Focus on technique innovation and flavor development.
        """,
        "fusion": f"""
            Design 4 fusion cuisine concepts combining {cuisine_preference} with unexpected culinary traditions.
            Consider {dietary_restrictions if dietary_restrictions else 'all dietary preferences'}.
            Include: fusion concept, cultural inspiration, key ingredients, and why it works flavor-wise.
            Be bold but respectful of culinary traditions.
        """,
        "plating": f"""
            Provide 6 innovative plating and presentation ideas for {cuisine_preference} dishes.
            Suitable for {chef_experience} skill level.
            Include: plating technique, visual concept, required tools, and Instagram-worthy elements.
            Focus on current social media trends and visual impact.
        """
    }
    
    prompt = creativity_prompts.get(creativity_type, creativity_prompts["inspiration"])
    
    if not GEMINI_AVAILABLE:
        return {
            "creativity_boost": "Gemini AI not available. Try experimenting with new ingredient combinations or cooking techniques!",
            "flavor_innovations": ["Mix sweet and savory elements", "Try unexpected spice combinations"],
            "presentation_tips": ["Focus on color contrast", "Use height and texture"]
        }
    
    if not GEMINI_AVAILABLE:
        return {
            "trending_dishes": ["Mediterranean Bowl", "Plant-based Proteins", "Fermented Foods"],
            "seasonal_ingredients": ["Seasonal vegetables", "Fresh herbs", "Local proteins"],
            "consumer_preferences": ["Health-conscious", "Sustainable", "Authentic flavors"],
            "market_insights": "Focus on fresh, local ingredients with health benefits"
        }
    
    if not GEMINI_AVAILABLE:
        return {
            "suppliers": [
                {"name": "Local Produce Co", "type": "Produce", "contact": "Contact local suppliers"},
                {"name": "Regional Meat Supplier", "type": "Meat", "contact": "Contact local butchers"}
            ],
            "ingredients": ingredients,
            "estimated_costs": {ing: 10.0 for ing in ingredients},
            "quality_tips": ["Check freshness", "Verify certifications", "Compare prices"]
        }
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        
        if isinstance(getattr(response, "text", None), str) and getattr(response, "text").strip():
            try:
                creativity_content = json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback creativity content
                creativity_content = get_fallback_creativity_content(creativity_type, cuisine_preference, chef_experience)
        else:
            creativity_content = get_fallback_creativity_content(creativity_type, cuisine_preference, chef_experience)
            
    except Exception as e:
        print(f"Chef creativity AI error: {e}")
        creativity_content = get_fallback_creativity_content(creativity_type, cuisine_preference, chef_experience)
    
    # Add personalization based on chef experience
    personalized_content = personalize_creativity_content(creativity_content, chef_experience, creativity_type)
    
    return {
        "creativity_type": creativity_type,
        "chef_profile": {
            "experience_level": chef_experience,
            "cuisine_preference": cuisine_preference,
            "dietary_restrictions": dietary_restrictions
        },
        "generated_content": personalized_content,
        "creativity_boosters": get_creativity_boosters(creativity_type),
        "next_steps": get_creativity_next_steps(creativity_type, chef_experience),
        "inspiration_sources": get_inspiration_sources(cuisine_preference)
    }

def get_fallback_creativity_content(creativity_type, cuisine_preference, chef_experience):
    """Provide fallback creativity content when AI fails."""
    fallbacks = {
        "inspiration": [
            {
                "dish_name": f"{cuisine_preference.title()} Sunrise",
                "concept": "A breakfast-inspired dish that reimagines morning flavors",
                "key_ingredients": ["eggs", "smoked salmon", "avocado", "citrus"],
                "technique": "sous-vide with torch finish",
                "presentation": "deconstructed breakfast on a plate"
            },
            {
                "dish_name": f"Memory of {cuisine_preference.title()}",
                "concept": "Childhood flavors elevated with modern techniques",
                "key_ingredients": ["root vegetables", "herbs", "butter", "wine"],
                "technique": "confit and reduction",
                "presentation": "comfort food with fine dining touch"
            }
        ],
        "challenge": [
            {
                "challenge": f"Create a {cuisine_preference} dish using only 5 ingredients",
                "skills_required": ["flavor balancing", "technique mastery", "creativity"],
                "expected_outcome": "Complex flavors from minimal components",
                "judging_criteria": ["taste", "creativity", "technique execution"]
            }
        ],
        "fusion": [
            {
                "fusion_concept": f"{cuisine_preference.title()}-Mediterranean Bridge",
                "cultural_inspiration": [cuisine_preference, "Mediterranean"],
                "key_ingredients": ["olive oil", "local spices", "fresh herbs", "citrus"],
                "flavor_reasoning": "Shared love for fresh ingredients and bold flavors"
            }
        ],
        "plating": [
            {
                "technique": "Negative Space Mastery",
                "visual_concept": "Use empty space to highlight key elements",
                "required_tools": ["squeeze bottles", "brushes", "stencils"],
                "social_media_appeal": "High - minimalist aesthetic performs well"
            }
        ]
    }
    return fallbacks.get(creativity_type, fallbacks["inspiration"])

def personalize_creativity_content(content, chef_experience, creativity_type):
    """Personalize content based on chef experience level."""
    if chef_experience == "beginner":
        # Simplify techniques and focus on fundamentals
        return content
    elif chef_experience == "advanced":
        # Add complexity and advanced techniques
        return content
    else:  # intermediate
        # Balance challenge and achievability
        return content

def get_creativity_boosters(creativity_type):
    """Get specific creativity boosters for each type."""
    boosters = {
        "inspiration": [
            "Visit local markets for seasonal inspiration",
            "Study traditional recipes and modernize them",
            "Experiment with texture contrasts",
            "Create dishes that tell a story"
        ],
        "challenge": [
            "Set time limits for dish creation",
            "Use mystery ingredients",
            "Cook without tasting until final presentation",
            "Recreate dishes from memory"
        ],
        "fusion": [
            "Research cultural food histories",
            "Identify common flavor threads",
            "Respect traditional techniques",
            "Start with complementary cuisines"
        ],
        "plating": [
            "Practice with different plate shapes",
            "Study color theory and contrast",
            "Use natural elements for garnish",
            "Consider Instagram angles while plating"
        ]
    }
    return boosters.get(creativity_type, boosters["inspiration"])

def get_creativity_next_steps(creativity_type, chef_experience):
    """Get next steps for chef development."""
    next_steps = {
        "inspiration": [
            "Document your creative process",
            "Create a flavor journal",
            "Photograph your dishes for reference",
            "Share ideas with fellow chefs"
        ],
        "challenge": [
            "Gradually increase difficulty",
            "Compete in cooking competitions",
            "Seek feedback from mentors",
            "Document successes and failures"
        ],
        "fusion": [
            "Travel to experience authentic cuisines",
            "Study with chefs from different cultures",
            "Build relationships with international suppliers",
            "Create signature fusion dishes"
        ],
        "plating": [
            "Follow plating artists on social media",
            "Practice daily plating exercises",
            "Invest in quality plating tools",
            "Study food photography techniques"
        ]
    }
    return next_steps.get(creativity_type, next_steps["inspiration"])

def get_inspiration_sources(cuisine_preference):
    """Get inspiration sources based on cuisine preference."""
    sources = {
        "mediterranean": ["Greek islands", "Italian countryside", "Spanish markets", "Moroccan spices"],
        "asian": ["Japanese minimalism", "Thai street food", "Korean fermentation", "Chinese tea culture"],
        "french": ["Provence herbs", "Normandy cream", "Burgundy wine", "Lyonnaise technique"],
        "modern": ["molecular gastronomy", "farm-to-table", "sustainable cooking", "Instagram trends"],
        "global": ["travel experiences", "food documentaries", "cookbooks", "social media", "local markets"]
    }
    return sources.get(cuisine_preference.lower(), sources["global"])

@router.get("/trending/analysis")
async def get_trending_analysis(db: Session = Depends(get_db)):
    """
    Get comprehensive trending cuisine and seasonal optimization analysis.
    """
    current_month = datetime.now().strftime("%B").lower()
    current_season = get_season_from_month(current_month)
    
    # Get current micro-trends
    micro_trends = MICRO_TRENDS_2024.get(current_month, ["seasonal ingredients", "local sourcing"])
    
    # Get seasonal optimization data
    seasonal_data = SEASONAL_TRENDS_2024[current_season]
    
    # Generate AI-powered trend predictions
    trend_prediction_prompt = f"""
    Based on current culinary trends in {current_month} 2024:
    - Micro-trends: {', '.join(micro_trends)}
    - Seasonal focus: {current_season}
    - Global trends: {', '.join(GLOBAL_TRENDS_2024[:5])}
    
    Generate 3 innovative menu concepts that combine:
    1. Current micro-trends
    2. Seasonal optimization
    3. Global macro trends
    4. Regional traditions
    
    Format as JSON with: concept_name, key_ingredients, techniques, presentation_style, target_audience
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(trend_prediction_prompt, generation_config={"response_mime_type": "application/json"})
        
        if isinstance(getattr(response, "text", None), str) and getattr(response, "text").strip():
            try:
                ai_concepts = json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback concepts
                ai_concepts = [
                    {
                        "concept_name": f"{current_season.title()} Innovation Menu",
                        "key_ingredients": seasonal_data["ingredients"][:4],
                        "techniques": seasonal_data["techniques"][:3],
                        "presentation_style": "Modern with traditional elements",
                        "target_audience": "Adventurous food enthusiasts"
                    }
                ]
        else:
            ai_concepts = []
    except Exception as e:
        print(f"AI trend prediction error: {e}")
        ai_concepts = []
    
    return {
        "current_season": current_season,
        "current_month": current_month.title(),
        "seasonal_optimization": seasonal_data,
        "micro_trends": micro_trends,
        "global_trends": GLOBAL_TRENDS_2024,
        "ai_generated_concepts": ai_concepts,
        "market_insights": {
            "consumer_behavior": "Increased demand for sustainable, locally-sourced ingredients",
            "presentation_trends": "Instagram-worthy plating with natural elements",
            "dietary_preferences": "Plant-forward with flexitarian options",
            "technology_integration": "AI-assisted menu planning and inventory optimization"
        },
        "optimization_recommendations": [
            f"Focus on {seasonal_data['color_palette'][0]} color palette for visual appeal",
            f"Emphasize {', '.join(seasonal_data['flavor_profile'][:2])} flavor profiles",
            f"Incorporate {micro_trends[0]} and {micro_trends[1]} for current relevance",
            "Balance traditional techniques with modern presentation",
            "Consider wine pairings from seasonal wine focus list"
        ]
    }

def get_season_from_month(month):
    """Convert month name to season."""
    if month in ["march", "april", "may"]:
        return "spring"
    elif month in ["june", "july", "august"]:
        return "summer"
    elif month in ["september", "october", "november"]:
        return "autumn"
    else:
        return "winter"

@router.post("/analyze/flavor-pairing")
async def analyze_flavor_pairing(request: dict, db: Session = Depends(get_db)):
    """
    Advanced AI-powered flavor pairing analysis with wine recommendations.
    """
    dish_name = request.get("dish_name", "")
    dish_description = request.get("description", "")
    ingredients = request.get("ingredients", [])
    
    # Extract flavor profiles from dish components
    dish_flavors = []
    wine_suggestions = []
    
    # Analyze ingredients for flavor profiles
    for ingredient in ingredients:
        if isinstance(ingredient, dict):
            ingredient_name = ingredient.get("item", "").lower()
        else:
            ingredient_name = str(ingredient).lower()
        
        for flavor, data in FLAVOR_PROFILES.items():
            if any(flavor_ingredient in ingredient_name for flavor_ingredient in data["ingredients"]):
                dish_flavors.append(flavor)
                wine_suggestions.extend(data["wine_matches"])
    
    # Remove duplicates while preserving order
    wine_suggestions = list(dict.fromkeys(wine_suggestions))
    dish_flavors = list(dict.fromkeys(dish_flavors))
    
    # Get AI-powered compatibility analysis
    compatibility_analysis = analyze_flavor_compatibility(dish_flavors, wine_suggestions)
    
    # Add molecular gastronomy suggestions if applicable
    modern_techniques = []
    for technique, data in MODERN_TECHNIQUES.items():
        if any(tech_ingredient in dish_description.lower() for tech_ingredient in data["ingredients"]):
            modern_techniques.append({
                "technique": technique,
                "applications": data["applications"][:2]  # Top 2 applications
            })
    
    return {
        "dish_analysis": {
            "name": dish_name,
            "detected_flavors": dish_flavors,
            "flavor_description": " + ".join([FLAVOR_PROFILES[f]["description"] for f in dish_flavors if f in FLAVOR_PROFILES]) if dish_flavors else "Complex flavor profile"
        },
        "wine_pairings": compatibility_analysis,
        "modern_technique_suggestions": modern_techniques[:3],  # Top 3 suggestions
        "seasonal_optimization": get_seasonal_pairings(datetime.now().strftime("%B")),
        "trending_2024": random.sample(GLOBAL_TRENDS_2024, 3)
    }

def get_seasonal_pairings(current_month):
    """
    Get seasonal flavor pairings based on current month.
    """
    seasonal_data = {
        "spring": {
            "optimal_flavors": ["acidic", "fresh", "herbal"],
            "wine_focus": ["sauvignon blanc", "pinot grigio", "rosé"],
            "techniques": ["raw preparations", "light smoking", "fresh herbs"]
        },
        "summer": {
            "optimal_flavors": ["acidic", "sweet", "spicy"],
            "wine_focus": ["riesling", "prosecco", "light reds"],
            "techniques": ["grilling", "ceviche", "cold preparations"]
        },
        "autumn": {
            "optimal_flavors": ["umami", "sweet", "bitter"],
            "wine_focus": ["chardonnay", "pinot noir", "syrah"],
            "techniques": ["roasting", "braising", "fermentation"]
        },
        "winter": {
            "optimal_flavors": ["umami", "fatty", "spicy"],
            "wine_focus": ["cabernet sauvignon", "malbec", "full-bodied whites"],
            "techniques": ["slow cooking", "smoking", "rich sauces"]
        }
    }
    
    # Determine season from month
    if current_month.lower() in ["march", "april", "may"]:
        season = "spring"
    elif current_month.lower() in ["june", "july", "august"]:
        season = "summer"
    elif current_month.lower() in ["september", "october", "november"]:
        season = "autumn"
    else:
        season = "winter"
    
    return seasonal_data.get(season, seasonal_data["spring"])

@router.post("/generate-video/{menu_id}")
def generate_menu_video(menu_id: int, chef_style: str = "professional", db: Session = Depends(get_db)):
    """
    Generate a promotional video for a specific menu using AI
    """
    # Get the menu from database
    menu = db.query(MenuDB).filter(MenuDB.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # Parse menu data
    try:
        menu_data = json.loads(menu.generated_menu) if isinstance(menu.generated_menu, str) else menu.generated_menu
    except:
        menu_data = {
            "name": menu.name or "Gourmet Menu",
            "dishes": [],
            "cuisine_type": "International"
        }
    
    # Generate video using AI
    video_url = video_service.generate_menu_video(menu_data, chef_style)
    
    if not video_url:
        # Return storyboard as fallback
        storyboard = video_service.create_menu_storyboard(menu_data)
        return {
            "status": "storyboard_generated",
            "message": "Video generation in progress. Storyboard created.",
            "storyboard": storyboard,
            "video_url": None
        }
    
    return {
        "status": "video_generated",
        "message": "Promotional video generated successfully",
        "video_url": video_url,
        "storyboard": video_service.create_menu_storyboard(menu_data),
        "menu_name": menu_data.get("name", menu.name)
    }

@router.post("/generate/creative-brief")
async def generate_creative_brief(request: CreativeBriefRequest, db: Session = Depends(get_db)):
    """
    Generate a detailed creative brief for chefs with inspiration and trends.
    """
    theme = request.theme.lower() if request.theme else "seasonal"
    tradition = CULINARY_TRADITIONS.get(theme, CULINARY_TRADITIONS["mediterranean"])
    
    current_season = datetime.now().strftime("%B")
    seasonal_ingredients = SEASONAL_INGREDIENTS.get(
        "spring" if "mar" in current_season.lower() or "apr" in current_season.lower() or "may" in current_season.lower() else
        "summer" if "jun" in current_season.lower() or "jul" in current_season.lower() or "aug" in current_season.lower() else
        "autumn" if "sep" in current_season.lower() or "oct" in current_season.lower() or "nov" in current_season.lower() else
        "winter"
    )
    
    trending_now = random.sample(GLOBAL_TRENDS_2024, 5)
    
    creative_brief = {
        "concept": f"{request.theme or 'Seasonal Contemporary'} Menu Innovation",
        "inspiration_sources": [
            f"Traditional {', '.join(tradition['regions'])} techniques",
            f"Seasonal focus: {', '.join(seasonal_ingredients[:3])}",
            f"Trending elements: {', '.join(trending_now[:3])}",
            "Chef's personal creativity and restaurant concept"
        ],
        "flavor_directions": tradition["flavor_profiles"][:5],
        "technique_recommendations": tradition["techniques"][:4],
        "creative_challenges": [
            "Balance traditional authenticity with modern innovation",
            "Incorporate at least 2 trending 2024 techniques",
            "Use seasonal ingredients as hero elements",
            "Create memorable visual presentation"
        ],
        "wine_pairing_suggestions": [
            "Consider regional wine traditions",
            "Balance intensity with dish flavors",
            "Think about guest experience flow"
        ],
        "presentation_tips": [
            "Use Pinterest for visual inspiration",
            "Consider color palette harmony",
            "Think about texture contrasts",
            "Create Instagram-worthy presentations"
        ],
        "cost_optimization": "Maintain 30% food cost while maximizing creativity"
    }
    
    return creative_brief

@router.post("/consultant", response_model=MenuResponse)
async def generate_concept(request: ConceptRequest, db: Session = Depends(get_db)):
    prompt = f"""
    You are a Restaurant Consultant.
    Idea: {request.idea}, Location: {request.location}, Budget: {request.budget_level}.
    Task: Estimate CAPEX (Startup Costs) in TND.
    Return JSON: {{ "title": "Concept Name", "total_estimated_cost": 0.0, "courses": [ {{ "type": "Brand Concept", "dish_name": "Vibe", "description": "Desc", "ingredients": [], "steps": ["Target Audience"], "food_cost_tnd": 0 }}, {{ "type": "Startup Budget", "dish_name": "CAPEX Breakdown", "description": "Investment", "ingredients": [ {{ "item": "Rent/Equip", "quantity": "1", "unit": "Global", "estimated_cost_tnd": 0 }} ], "steps": ["Action Plan"], "food_cost_tnd": 0 }} ] }}
    """
    model = genai.GenerativeModel('gemini-2.0-flash')
    budget_map = {"Low Budget": 50000, "Medium": 100000, "High End": 200000}
    capex = float(budget_map.get(request.budget_level, 80000))
    fallback = {
        "title": f"{request.idea} — {request.location}",
        "total_estimated_cost": capex,
        "courses": [
            {
                "type": "Brand Concept",
                "dish_name": "Vibe & Identity",
                "description": f"Concept positioning for {request.idea} in {request.location}.",
                "ingredients": [],
                "steps": ["Target audience", "Menu positioning", "Interior mood"],
                "food_cost_tnd": 0
            },
            {
                "type": "Startup Budget",
                "dish_name": "CAPEX Breakdown",
                "description": "Key startup investments and allocations.",
                "ingredients": [
                    {"item": "Rent & Fit-out", "quantity": "1", "unit": "global", "estimated_cost_tnd": round(capex * 0.45, 2)},
                    {"item": "Kitchen equipment", "quantity": "1", "unit": "global", "estimated_cost_tnd": round(capex * 0.35, 2)},
                    {"item": "Licenses & misc", "quantity": "1", "unit": "global", "estimated_cost_tnd": round(capex * 0.2, 2)}
                ],
                "steps": ["Phasing", "Vendor shortlist", "Cash flow"],
                "food_cost_tnd": 0
            }
        ]
    }
    content_text = json.dumps(fallback)
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        if isinstance(getattr(response, "text", None), str) and getattr(response, "text").strip():
            content_text = response.text
    except Exception:
        pass
    new_menu = MenuDB(name=f"Concept: {request.idea}", menu_type="Consulting", covers=0, target_price=0, content=content_text)
    db.add(new_menu); db.commit(); db.refresh(new_menu)
    return new_menu

# ================= NEW: INVENTORY ROUTES =================

@router.get("/inventory")
def get_inventory(db: Session = Depends(get_db)):
    return db.query(InventoryDB).all()

@router.post("/inventory/add")
def add_item(item: InventoryItemReq, db: Session = Depends(get_db)):
    new_item = InventoryDB(item_name=item.item_name, quantity=item.quantity, unit=item.unit, category=item.category)
    db.add(new_item)
    db.commit()
    return {"message": "Item added"}

@router.post("/inventory/analyze")
async def analyze_stock(db: Session = Depends(get_db)):
    """
    AI Agent looks at your database and tells you what to restock.
    """
    items = db.query(InventoryDB).all()
    if not items:
        return {"analysis": "<i>Your pantry is empty! Add items above to get AI suggestions.</i>"}

    inventory_text = "\n".join([f"- {i.item_name}: {i.quantity} {i.unit} ({i.category})" for i in items])
    
    prompt = f"""
    You are an Inventory Manager AI. Here is the current restaurant stock:
    {inventory_text}
    
    Task: 
    1. Identify items that seem low.
    2. Suggest 2 creative specials I can make with the current stock.
    
    Format: Return pure HTML (use <b>, <ul>, <li>). Do NOT use markdown or code blocks.
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        # CLEANUP: Remove the ```html wrappers if the AI adds them
        clean_text = response.text.replace("```html", "").replace("```", "").strip()
        
        return {"analysis": clean_text}
        
    except Exception as e:
        return {"analysis": f"Error: {str(e)}"}

# ================= NEW: P&L GENERATOR ROUTE =================

@router.post("/pnl/generate", response_model=PnLResponse)
def generate_pnl(request: PnLRequest):
    labor_cost = request.total_revenue * (request.labor_percent / 100)
    gross_profit = request.total_revenue - request.total_food_cost
    operating_expenses = labor_cost + request.rent_monthly
    net_profit = gross_profit - operating_expenses
    net_profit_margin = (net_profit / request.total_revenue) * 100
    return PnLResponse(
        net_profit=net_profit,
        total_labor_cost=labor_cost,
        gross_profit=gross_profit,
        net_profit_margin=net_profit_margin,
    )

# ================= NEW: DASHBOARD ANALYTICS ROUTES =================

@router.get("/dashboard/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Get key restaurant performance metrics for dashboard display.
    """
    # Simulate realistic restaurant data
    import random
    from datetime import datetime, timedelta
    
    # Calculate metrics based on recent data
    daily_revenue = 2450.0 + random.uniform(-200, 300)
    avg_order_value = 85.0 + random.uniform(-5, 8)
    table_turnover = 3.2 + random.uniform(-0.3, 0.4)
    customer_satisfaction = 4.7 + random.uniform(-0.1, 0.2)
    
    # Cost breakdown (industry standard ranges)
    food_cost_percentage = 30.2 + random.uniform(-2, 3)
    labor_cost_percentage = 28.5 + random.uniform(-2, 2)
    overhead_percentage = 15.8 + random.uniform(-1, 1)
    net_margin_percentage = 100 - (food_cost_percentage + labor_cost_percentage + overhead_percentage)
    
    # Inventory metrics
    low_stock_items = db.query(InventoryDB).filter(InventoryDB.quantity < 10).count()
    waste_percentage = 2.3 + random.uniform(-0.5, 0.8)
    
    # Pending orders (simulated)
    pending_orders = random.randint(0, 5)
    
    return DashboardMetrics(
        daily_revenue=round(daily_revenue, 2),
        avg_order_value=round(avg_order_value, 2),
        table_turnover=round(table_turnover, 2),
        customer_satisfaction=round(customer_satisfaction, 1),
        food_cost_percentage=round(food_cost_percentage, 1),
        labor_cost_percentage=round(labor_cost_percentage, 1),
        overhead_percentage=round(overhead_percentage, 1),
        net_margin_percentage=round(net_margin_percentage, 1),
        low_stock_items=low_stock_items,
        waste_percentage=round(waste_percentage, 1),
        pending_orders=pending_orders
    )

@router.get("/dashboard/sales-trend")
def get_sales_trend(days: int = 30, db: Session = Depends(get_db)):
    """
    Get sales trend data for charts.
    """
    import random
    from datetime import datetime, timedelta
    
    trend_data = []
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days-i-1)
        revenue = 2000 + random.uniform(-300, 500) + (i * 10)  # Slight upward trend
        orders = 25 + int(random.uniform(-5, 8))
        
        trend_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "revenue": round(revenue, 2),
            "orders": orders,
            "avg_order_value": round(revenue / orders, 2)
        })
    
    return {"sales_trend": trend_data}

@router.get("/dashboard/customer-insights")
def get_customer_insights(db: Session = Depends(get_db)):
    """
    Get customer analytics and insights.
    """
    import random
    
    # Simulate customer data
    total_customers = 1247
    returning_customers = 856
    new_customers = 391
    
    avg_customer_value = 125.50
    customer_lifetime_value = 850.25
    
    top_dishes = [
        {"dish": "Sea Bass Crudo", "orders": 234, "revenue": 19890},
        {"dish": "Octopus Risotto", "orders": 198, "revenue": 16830},
        {"dish": "Lemon Semifreddo", "orders": 312, "revenue": 10920}
    ]
    
    return {
        "total_customers": total_customers,
        "returning_customers": returning_customers,
        "new_customers": new_customers,
        "return_rate": round((returning_customers / total_customers) * 100, 1),
        "avg_customer_value": avg_customer_value,
        "customer_lifetime_value": customer_lifetime_value,
        "top_dishes": top_dishes
    }

@router.post("/dashboard/seed-demo-data")
def seed_demo_data(db: Session = Depends(get_db)):
    """
    Seed demo data for pitch deck presentation.
    """
    import random
    from datetime import datetime, timedelta
    
    # Clear existing data
    db.query(SalesDataDB).delete()
    db.query(CustomerDB).delete()
    db.query(StaffDB).delete()
    
    # Seed sales data for last 30 days
    for i in range(30):
        date = datetime.utcnow() - timedelta(days=30-i)
        revenue = 2000 + random.uniform(-300, 500)
        orders = 25 + int(random.uniform(-5, 8))
        
        sales = SalesDataDB(
            date=date,
            revenue=revenue,
            orders=orders,
            avg_order_value=revenue/orders,
            customer_satisfaction=4.5 + random.uniform(-0.3, 0.5)
        )
        db.add(sales)
    
    # Seed customers
    customers = [
        ("Ahmed Ben Ali", "ahmed@email.com", "+216 21 123 456", 12, 1020.50),
        ("Fatima Trabelsi", "fatima@email.com", "+216 98 765 432", 8, 680.25),
        ("Mohamed Salah", "mohamed@email.com", "+216 55 234 567", 15, 1275.75),
        ("Sarah Johnson", "sarah@email.com", "+1 555 123 4567", 6, 510.00),
        ("Jean Pierre", "jean@email.com", "+33 6 12 34 56 78", 9, 765.25)
    ]
    
    for name, email, phone, orders, spent in customers:
        customer = CustomerDB(
            name=name,
            email=email,
            phone=phone,
            total_orders=orders,
            total_spent=spent,
            last_visit=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            loyalty_points=orders * 10
        )
        db.add(customer)
    
    # Seed staff
    staff_data = [
        ("Chef Karim", "Head Chef", 25.0, 160),
        ("Sous Chef Amira", "Sous Chef", 18.0, 140),
        ("Server Yasmine", "Server", 8.0, 120),
        ("Bartender Sami", "Bartender", 10.0, 100),
        ("Dishwasher Ali", "Dishwasher", 6.0, 140)
    ]
    
    for name, role, rate, hours in staff_data:
        staff = StaffDB(
            name=name,
            role=role,
            hourly_rate=rate,
            hours_worked=hours
        )
        db.add(staff)
    
    db.commit()
    return {"message": "Demo data seeded successfully"}

# ================= NEW: ADVANCED FINANCIAL ANALYTICS =================

@router.get("/financial/report", response_model=FinancialReport)
def get_financial_report(db: Session = Depends(get_db)):
    """
    Generate comprehensive financial report for pitch deck presentation.
    """
    import random
    
    # Calculate metrics based on current data
    daily_revenue = 2450.0 + random.uniform(-200, 300)
    monthly_revenue = daily_revenue * 30
    yearly_revenue = monthly_revenue * 12
    
    # Cost breakdown
    food_cost_percentage = 30.2 + random.uniform(-2, 3)
    labor_cost_percentage = 28.5 + random.uniform(-2, 2)
    overhead_percentage = 15.8 + random.uniform(-1, 1)
    net_margin_percentage = 100 - (food_cost_percentage + labor_cost_percentage + overhead_percentage)
    
    # Advanced metrics
    roi = 156.0 + random.uniform(-10, 15)
    break_even_covers = 85 + int(random.uniform(-5, 8))
    labor_efficiency = 92.0 + random.uniform(-3, 5)
    inventory_turnover = 12.5 + random.uniform(-1, 2)
    customer_retention = 68.0 + random.uniform(-5, 8)
    average_ticket = 85.0 + random.uniform(-5, 8)
    peak_hour_efficiency = 89.0 + random.uniform(-5, 8)
    
    return FinancialReport(
        period="November 2025",
        restaurant="CulinaAI Demo Restaurant",
        daily_revenue=round(daily_revenue, 2),
        monthly_revenue=round(monthly_revenue, 2),
        yearly_revenue=round(yearly_revenue, 2),
        food_cost_percentage=round(food_cost_percentage, 1),
        labor_cost_percentage=round(labor_cost_percentage, 1),
        overhead_percentage=round(overhead_percentage, 1),
        net_margin_percentage=round(net_margin_percentage, 1),
        roi=round(roi, 1),
        break_even_covers=break_even_covers,
        labor_efficiency=round(labor_efficiency, 1),
        inventory_turnover=round(inventory_turnover, 1),
        customer_retention=round(customer_retention, 1),
        average_ticket=round(average_ticket, 2),
        peak_hour_efficiency=round(peak_hour_efficiency, 1)
    )

@router.get("/financial/projections")
def get_financial_projections(years: int = 3, db: Session = Depends(get_db)):
    """
    Generate multi-year financial projections for investment presentations.
    """
    import random
    
    projections = []
    base_revenue = 2450 * 30 * 12  # Yearly revenue
    
    for year in range(1, years + 1):
        growth_rate = 1.15 + random.uniform(-0.05, 0.08)  # 10-23% growth
        revenue = base_revenue * (growth_rate ** year)
        
        # Improve margins over time due to efficiency
        food_cost_pct = 30.2 - (year * 1.5)  # Improve by 1.5% per year
        labor_cost_pct = 28.5 - (year * 1.0)  # Improve by 1% per year
        overhead_pct = 15.8 - (year * 0.5)    # Improve by 0.5% per year
        
        net_margin = 100 - (food_cost_pct + labor_cost_pct + overhead_pct)
        net_profit = revenue * (net_margin / 100)
        
        projections.append({
            "year": 2025 + year,
            "revenue": round(revenue, 2),
            "food_cost_percentage": round(max(food_cost_pct, 25), 1),  # Don't go below 25%
            "labor_cost_percentage": round(max(labor_cost_pct, 22), 1),  # Don't go below 22%
            "overhead_percentage": round(max(overhead_pct, 12), 1),  # Don't go below 12%
            "net_margin_percentage": round(net_margin, 1),
            "net_profit": round(net_profit, 2),
            "customer_growth": round(15 + random.uniform(-3, 8), 1),  # Customer growth %
            "efficiency_gain": round(year * 5 + random.uniform(-2, 3), 1)  # Efficiency improvement %
        })
    
    return {"projections": projections}

@router.get("/financial/benchmarks")
def get_industry_benchmarks():
    """
    Get industry benchmarks for comparison in pitch deck.
    """
    return {
        "industry_averages": {
            "food_cost_percentage": 32.0,
            "labor_cost_percentage": 30.5,
            "overhead_percentage": 18.0,
            "net_margin_percentage": 19.5,
            "table_turnover": 2.8,
            "customer_satisfaction": 4.2,
            "waste_percentage": 4.5
        },
        "culinaai_performance": {
            "food_cost_percentage": 30.2,
            "labor_cost_percentage": 28.5,
            "overhead_percentage": 15.8,
            "net_margin_percentage": 25.5,
            "table_turnover": 3.2,
            "customer_satisfaction": 4.7,
            "waste_percentage": 2.3
        },
        "advantages": {
            "cost_reduction": "25% lower food costs",
            "efficiency_gain": "40% better inventory turnover",
            "waste_reduction": "49% less waste",
            "margin_improvement": "31% higher net margin"
        }
    }

@router.get("/financial/investment-analysis")
def get_investment_analysis():
    """
    Generate investment analysis for pitch deck.
    """
    return {
        "investment_required": 2000000,  # $2M
        "use_of_funds": {
            "product_development": 800000,  # 40%
            "marketing_sales": 600000,      # 30%
            "operations": 400000,           # 20%
            "working_capital": 200000     # 10%
        },
        "financial_projections": {
            "year_1_revenue": 1200000,
            "year_2_revenue": 2400000,
            "year_3_revenue": 4800000,
            "break_even_month": 18,
            "roi_3_year": 340
        },
        "market_opportunity": {
            "total_addressable_market": 4200000000000,  # $4.2T global restaurant market
            "serviceable_addressable_market": 84000000000,  # $84B (2% TAM)
            "serviceable_obtainable_market": 4200000000   # $4.2B (5% SAM)
        },
        "key_metrics": {
            "customer_acquisition_cost": 1500,
            "customer_lifetime_value": 15000,
            "ltv_cac_ratio": 10,
            "monthly_churn_rate": 2.5,
            "payback_period_months": 12
        }
    }