import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class NutritionalInfo:
    calories: float
    lipids: float  # fats in grams
    glucides: float  # carbohydrates in grams
    proteines: float  # proteins in grams
    fiber: float  # fiber in grams
    sodium: float  # sodium in mg
    portion_size: float  # portion size in grams

class NutritionService:
    def __init__(self):
        # Nutritional database for common ingredients (per 100g)
        self.nutrition_db = {
            # Proteins
            "chicken breast": {"calories": 165, "lipids": 3.6, "glucides": 0, "proteines": 31, "fiber": 0, "sodium": 74},
            "beef": {"calories": 250, "lipids": 15, "glucides": 0, "proteines": 26, "fiber": 0, "sodium": 60},
            "fish": {"calories": 206, "lipids": 12, "glucides": 0, "proteines": 22, "fiber": 0, "sodium": 61},
            "salmon": {"calories": 208, "lipids": 13, "glucides": 0, "proteines": 20, "fiber": 0, "sodium": 59},
            "shrimp": {"calories": 106, "lipids": 1.7, "glucides": 0, "proteines": 20, "fiber": 0, "sodium": 148},
            "eggs": {"calories": 155, "lipids": 11, "glucides": 1.1, "proteines": 13, "fiber": 0, "sodium": 142},
            
            # Vegetables
            "tomato": {"calories": 18, "lipids": 0.2, "glucides": 3.9, "proteines": 0.9, "fiber": 1.2, "sodium": 5},
            "onion": {"calories": 40, "lipids": 0.1, "glucides": 9.3, "proteines": 1.1, "fiber": 1.7, "sodium": 4},
            "garlic": {"calories": 149, "lipids": 0.5, "glucides": 33, "proteines": 6.4, "fiber": 2.1, "sodium": 17},
            "carrot": {"calories": 41, "lipids": 0.2, "glucides": 10, "proteines": 0.9, "fiber": 2.8, "sodium": 69},
            "potato": {"calories": 77, "lipids": 0.1, "glucides": 17, "proteines": 2, "fiber": 2.2, "sodium": 6},
            "lettuce": {"calories": 15, "lipids": 0.2, "glucides": 2.9, "proteines": 1.4, "fiber": 1.3, "sodium": 28},
            "spinach": {"calories": 23, "lipids": 0.4, "glucides": 3.6, "proteines": 2.9, "fiber": 2.2, "sodium": 79},
            "broccoli": {"calories": 34, "lipids": 0.4, "glucides": 7, "proteines": 2.8, "fiber": 2.6, "sodium": 33},
            "mushroom": {"calories": 22, "lipids": 0.3, "glucides": 3.3, "proteines": 3.1, "fiber": 1, "sodium": 5},
            
            # Fruits
            "lemon": {"calories": 29, "lipids": 0.3, "glucides": 9.3, "proteines": 1.1, "fiber": 2.8, "sodium": 2},
            "lime": {"calories": 30, "lipids": 0.2, "glucides": 11, "proteines": 0.7, "fiber": 2.8, "sodium": 2},
            "orange": {"calories": 47, "lipids": 0.1, "glucides": 12, "proteines": 0.9, "fiber": 2.4, "sodium": 0},
            "apple": {"calories": 52, "lipids": 0.2, "glucides": 14, "proteines": 0.3, "fiber": 2.4, "sodium": 1},
            
            # Grains and Legumes
            "rice": {"calories": 130, "lipids": 0.3, "glucides": 28, "proteines": 2.7, "fiber": 0.4, "sodium": 1},
            "pasta": {"calories": 131, "lipids": 1.1, "glucides": 25, "proteines": 5, "fiber": 1.8, "sodium": 6},
            "bread": {"calories": 265, "lipids": 3.2, "glucides": 49, "proteines": 9, "fiber": 2.7, "sodium": 491},
            "lentils": {"calories": 116, "lipids": 0.4, "glucides": 20, "proteines": 9, "fiber": 7.9, "sodium": 2},
            "chickpeas": {"calories": 164, "lipids": 2.6, "glucides": 27, "proteines": 8.9, "fiber": 7.6, "sodium": 7},
            
            # Dairy
            "butter": {"calories": 717, "lipids": 81, "glucides": 0.1, "proteines": 0.9, "fiber": 0, "sodium": 11},
            "cheese": {"calories": 113, "lipids": 9, "glucides": 1, "proteines": 7, "fiber": 0, "sodium": 621},
            "parmesan": {"calories": 431, "lipids": 29, "glucides": 4.1, "proteines": 38, "fiber": 0, "sodium": 1529},
            "milk": {"calories": 42, "lipids": 1, "glucides": 5, "proteines": 3.4, "fiber": 0, "sodium": 44},
            "cream": {"calories": 345, "lipids": 36, "glucides": 2.8, "proteines": 2.1, "fiber": 0, "sodium": 40},
            
            # Oils and Condiments
            "olive oil": {"calories": 884, "lipids": 100, "glucides": 0, "proteines": 0, "fiber": 0, "sodium": 2},
            "vegetable oil": {"calories": 884, "lipids": 100, "glucides": 0, "proteines": 0, "fiber": 0, "sodium": 0},
            "salt": {"calories": 0, "lipids": 0, "glucides": 0, "proteines": 0, "fiber": 0, "sodium": 38758},
            "pepper": {"calories": 251, "lipids": 3.3, "glucides": 64, "proteines": 10, "fiber": 25, "sodium": 20},
            
            # Herbs and Spices
            "parsley": {"calories": 36, "lipids": 0.8, "glucides": 6.3, "proteines": 3, "fiber": 3.3, "sodium": 56},
            "basil": {"calories": 23, "lipids": 0.6, "glucides": 2.7, "proteines": 3.2, "fiber": 1.6, "sodium": 4},
            "oregano": {"calories": 265, "lipids": 4.3, "glucides": 69, "proteines": 9, "fiber": 43, "sodium": 15},
            "thyme": {"calories": 276, "lipids": 7.4, "glucides": 63, "proteines": 9.1, "fiber": 37, "sodium": 9},
            
            # Seafood
            "tuna": {"calories": 144, "lipids": 4.9, "glucides": 0, "proteines": 25, "fiber": 0, "sodium": 47},
            "cod": {"calories": 82, "lipids": 0.7, "glucides": 0, "proteines": 18, "fiber": 0, "sodium": 120},
            "octopus": {"calories": 82, "lipids": 1, "glucides": 2.2, "proteines": 15, "fiber": 0, "sodium": 230},
            "calamari": {"calories": 92, "lipids": 1.4, "glucides": 3.1, "proteines": 15, "fiber": 0, "sodium": 44},
            
            # Mediterranean Specialties
            "couscous": {"calories": 112, "lipids": 0.2, "glucides": 23, "proteines": 3.8, "fiber": 1.4, "sodium": 5},
            "harissa": {"calories": 261, "lipids": 15, "glucides": 31, "proteines": 3.6, "fiber": 7.2, "sodium": 1200},
            "tahini": {"calories": 595, "lipids": 54, "glucides": 21, "proteines": 17, "fiber": 9.3, "sodium": 115},
            "feta cheese": {"calories": 264, "lipids": 21, "glucides": 4.1, "proteines": 14, "fiber": 0, "sodium": 1116},
            "olives": {"calories": 115, "lipids": 11, "glucides": 6.3, "proteines": 0.8, "fiber": 3.2, "sodium": 735},
            
            # Tunisian Specialties
            "merguez": {"calories": 257, "lipids": 21, "glucides": 1.6, "proteines": 16, "fiber": 0, "sodium": 800},
            "brik": {"calories": 268, "lipids": 17, "glucides": 23, "proteines": 5.5, "fiber": 1.2, "sodium": 400},
            "lablabi": {"calories": 145, "lipids": 2.1, "glucides": 22, "proteines": 9.8, "fiber": 7.9, "sodium": 380},
            "tagine": {"calories": 185, "lipids": 8.2, "glucides": 15, "proteines": 12, "fiber": 3.1, "sodium": 420},
            "chakchouka": {"calories": 95, "lipids": 6.8, "glucides": 7.2, "proteines": 3.8, "fiber": 2.1, "sodium": 280}
        }
        
        # Common portion sizes in grams
        self.portion_sizes = {
            "appetizer": 80,
            "starter": 120,
            "main_course": 250,
            "side_dish": 100,
            "dessert": 80,
            "soup": 200,
            "salad": 150
        }
    
    def calculate_nutrition(self, ingredients: List[Dict[str, Any]], dish_type: str = "main_course") -> NutritionalInfo:
        """
        Calculate nutritional information for a dish based on ingredients
        
        Args:
            ingredients: List of ingredients with name, quantity, unit
            dish_type: Type of dish for portion sizing
        
        Returns:
            NutritionalInfo object with calculated values
        """
        total_nutrition = {
            "calories": 0,
            "lipids": 0,
            "glucides": 0,
            "proteines": 0,
            "fiber": 0,
            "sodium": 0
        }
        
        for ingredient in ingredients:
            ingredient_name = ingredient.get("item", "").lower()
            quantity = float(ingredient.get("quantity", 0))
            unit = ingredient.get("unit", "g").lower()
            
            # Convert to grams if needed
            weight_in_grams = self._convert_to_grams(quantity, unit, ingredient_name)
            
            # Find matching ingredient in database
            nutrition_data = self._find_ingredient_nutrition(ingredient_name)
            
            if nutrition_data:
                # Calculate nutrition for this ingredient (per 100g basis)
                multiplier = weight_in_grams / 100
                
                total_nutrition["calories"] += nutrition_data["calories"] * multiplier
                total_nutrition["lipids"] += nutrition_data["lipids"] * multiplier
                total_nutrition["glucides"] += nutrition_data["glucides"] * multiplier
                total_nutrition["proteines"] += nutrition_data["proteines"] * multiplier
                total_nutrition["fiber"] += nutrition_data["fiber"] * multiplier
                total_nutrition["sodium"] += nutrition_data["sodium"] * multiplier
        
        # Calculate portion size based on dish type
        portion_size = self.portion_sizes.get(dish_type, 200)
        
        # Adjust for actual total weight if we have enough ingredients
        estimated_total_weight = sum(self._convert_to_grams(float(ing.get("quantity", 0)), ing.get("unit", "g").lower(), ing.get("item", "").lower()) for ing in ingredients)
        if estimated_total_weight > 0:
            portion_size = min(estimated_total_weight, portion_size * 1.5)  # Cap at 1.5x standard portion
        
        return NutritionalInfo(
            calories=round(total_nutrition["calories"], 1),
            lipids=round(total_nutrition["lipids"], 1),
            glucides=round(total_nutrition["glucides"], 1),
            proteines=round(total_nutrition["proteines"], 1),
            fiber=round(total_nutrition["fiber"], 1),
            sodium=round(total_nutrition["sodium"], 1),
            portion_size=round(portion_size, 1)
        )
    
    def _convert_to_grams(self, quantity: float, unit: str, ingredient_name: str) -> float:
        """Convert various units to grams"""
        conversion_factors = {
            "g": 1,
            "gram": 1,
            "grams": 1,
            "kg": 1000,
            "kilogram": 1000,
            "kilograms": 1000,
            "ml": 1,  # Approximation for water-based liquids
            "milliliter": 1,
            "milliliters": 1,
            "l": 1000,
            "liter": 1000,
            "liters": 1000,
            "cup": 240,
            "cups": 240,
            "tbsp": 15,
            "tablespoon": 15,
            "tablespoons": 15,
            "tsp": 5,
            "teaspoon": 5,
            "teaspoons": 5,
            "oz": 28.35,
            "ounce": 28.35,
            "ounces": 28.35,
            "lb": 453.6,
            "pound": 453.6,
            "pounds": 453.6
        }
        
        # Handle "piece" or "unit" by using average weights
        if unit in ["piece", "pieces", "unit", "units", "clove", "cloves"]:
            average_weights = {
                "egg": 50,
                "eggs": 50,
                "tomato": 150,
                "onion": 100,
                "garlic clove": 3,
                "lemon": 85,
                "lime": 67,
                "orange": 131,
                "apple": 150,
                "potato": 150,
                "carrot": 61,
                "banana": 118,
                "avocado": 150,
                "mushroom": 20
            }
            
            ingredient_lower = ingredient_name.lower()
            for key, weight in average_weights.items():
                if key in ingredient_lower:
                    return weight * quantity
            
            # Default to 100g if unknown
            return 100 * quantity
        
        return quantity * conversion_factors.get(unit, 1)  # Default to grams
    
    def _find_ingredient_nutrition(self, ingredient_name: str) -> Optional[Dict[str, float]]:
        """Find the closest matching ingredient in the nutrition database"""
        ingredient_lower = ingredient_name.lower()
        
        # Direct match
        if ingredient_lower in self.nutrition_db:
            return self.nutrition_db[ingredient_lower]
        
        # Try partial matches
        for key, nutrition in self.nutrition_db.items():
            if key in ingredient_lower or ingredient_lower in key:
                return nutrition
        
        # Try to match by food category using keywords
        category_matches = {
            "meat": "beef",
            "poultry": "chicken breast",
            "fish": "fish",
            "seafood": "shrimp",
            "vegetable": "tomato",
            "fruit": "apple",
            "grain": "rice",
            "pasta": "pasta",
            "bread": "bread",
            "cheese": "cheese",
            "oil": "olive oil",
            "herb": "parsley",
            "spice": "pepper"
        }
        
        for category, default_ingredient in category_matches.items():
            if category in ingredient_lower:
                return self.nutrition_db.get(default_ingredient)
        
        # Return None if no match found (will be ignored in calculations)
        return None
    
    def calculate_dish_nutrition(self, dish_name: str, ingredients: List[Dict[str, Any]]) -> Optional[NutritionalInfo]:
        """
        Calculate nutritional information for a dish given its ingredients.
        This method is called by the backend menu generation.
        
        Args:
            dish_name: Name of the dish
            ingredients: List of ingredients with format [{'name': 'ingredient', 'quantity': 100, 'unit': 'g'}]
            
        Returns:
            NutritionalInfo object with calculated nutritional values
        """
        # Convert ingredient format to match the expected format for calculate_nutrition
        formatted_ingredients = []
        for ingredient in ingredients:
            formatted_ingredient = {
                'item': ingredient.get('name', ''),
                'quantity': str(ingredient.get('quantity', 0)),
                'unit': ingredient.get('unit', 'g')
            }
            formatted_ingredients.append(formatted_ingredient)
        
        # Determine dish type based on dish name
        dish_type = "main_course"
        dish_lower = dish_name.lower()
        if any(word in dish_lower for word in ['salad', 'soup', 'appetizer', 'starter']):
            dish_type = "appetizer"
        elif any(word in dish_lower for word in ['dessert', 'cake', 'pie', 'ice cream']):
            dish_type = "dessert"
        elif any(word in dish_lower for word in ['side', 'vegetable', 'potato', 'rice']):
            dish_type = "side_dish"
        
        return self.calculate_nutrition(formatted_ingredients, dish_type)

    def get_nutritional_recommendations(self, nutrition_info: NutritionalInfo) -> Dict[str, str]:
        """Provide nutritional recommendations based on calculated values"""
        recommendations = {}
        
        # Calorie recommendations
        if nutrition_info.calories < 200:
            recommendations["calories"] = "Low calorie - good for weight management"
        elif nutrition_info.calories < 400:
            recommendations["calories"] = "Moderate calorie - balanced portion"
        elif nutrition_info.calories < 600:
            recommendations["calories"] = "High calorie - substantial meal"
        else:
            recommendations["calories"] = "Very high calorie - consider portion size"
        
        # Macronutrient balance
        total_macros = nutrition_info.lipids + nutrition_info.glucides + nutrition_info.proteines
        if total_macros > 0:
            fat_percentage = (nutrition_info.lipids * 9) / nutrition_info.calories * 100
            carb_percentage = (nutrition_info.glucides * 4) / nutrition_info.calories * 100
            protein_percentage = (nutrition_info.proteines * 4) / nutrition_info.calories * 100
            
            if fat_percentage > 35:
                recommendations["lipids"] = "High fat content - consider reducing oil/butter"
            elif fat_percentage < 15:
                recommendations["lipids"] = "Low fat - good for heart health"
            else:
                recommendations["lipids"] = "Balanced fat content"
            
            if carb_percentage > 60:
                recommendations["glucides"] = "High carbohydrates - energy-rich meal"
            elif carb_percentage < 30:
                recommendations["glucides"] = "Low carbohydrates - suitable for low-carb diets"
            else:
                recommendations["glucides"] = "Balanced carbohydrate content"
            
            if protein_percentage > 25:
                recommendations["proteines"] = "High protein - excellent for muscle building"
            elif protein_percentage < 10:
                recommendations["proteines"] = "Low protein - consider adding protein sources"
            else:
                recommendations["proteines"] = "Adequate protein content"
        
        # Sodium recommendations
        if nutrition_info.sodium > 400:
            recommendations["sodium"] = "High sodium - consider reducing salt"
        elif nutrition_info.sodium < 100:
            recommendations["sodium"] = "Low sodium - heart-healthy choice"
        else:
            recommendations["sodium"] = "Moderate sodium content"
        
        # Fiber recommendations
        if nutrition_info.fiber > 5:
            recommendations["fiber"] = "High fiber - excellent for digestion"
        elif nutrition_info.fiber < 2:
            recommendations["fiber"] = "Low fiber - consider adding vegetables"
        else:
            recommendations["fiber"] = "Good fiber content"
        
        return recommendations

# Global instance
nutrition_service = NutritionService()