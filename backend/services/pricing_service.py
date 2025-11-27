"""
Real-time pricing service for ingredient cost calculations
Integrates with multiple international pricing APIs
"""

import requests
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import aiohttp
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class PricingService:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = timedelta(hours=6)
        self.session = None
        
        # API configurations for different regions
        self.api_configs = {
            'tunisia': {
                'primary': {
                    'url': 'https://api.openfoodfacts.org/api/v2/search',
                    'params': {'countries': 'Tunisia', 'fields': 'product_name,price,quantity'}
                },
                'backup': {
                    'url': 'https://world.openfoodfacts.org/api/v2/search',
                    'params': {'countries': 'Tunisia', 'fields': 'product_name,price,quantity'}
                }
            },
            'mediterranean': {
                'primary': {
                    'url': 'https://api.openfoodfacts.org/api/v2/search',
                    'params': {'countries': 'Italy,Spain,Greece,Tunisia', 'fields': 'product_name,price,quantity'}
                }
            },
            'global': {
                'primary': {
                    'url': 'https://api.openfoodfacts.org/api/v2/search',
                    'params': {'fields': 'product_name,price,quantity,categories'}
                }
            }
        }
        
        # Ingredient mapping for common culinary ingredients
        self.ingredient_mapping = {
            'sea bass': ['sea bass', 'bar', 'loup de mer', 'spigola'],
            'octopus': ['octopus', 'poulpe', 'polpo', 'pulpo'],
            'saffron': ['saffron', 'safran', 'zafferano'],
            'lemon': ['lemon', 'citron', 'limone', 'limón'],
            'citrus': ['citrus', 'agrumes', 'agrume'],
            'herb oil': ['herb oil', 'huile aux herbes', 'olio alle erbe'],
            'microgreens': ['microgreens', 'micro pousses', 'micro verdure'],
            'risotto': ['risotto rice', 'riz pour risotto', 'riso per risotto'],
            'fennel': ['fennel', 'fenouil', 'finocchio', 'hinojo'],
            'almond': ['almond', 'amande', 'mandorla', 'almendra'],
            'semifreddo': ['semifreddo', 'semi-freddo', 'semifreddo base']
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def get_cache_key(self, ingredient: str, region: str = 'tunisia') -> str:
        return f"{ingredient}:{region}:{datetime.now().strftime('%Y-%m-%d')}"

    def is_cache_valid(self, cache_key: str) -> bool:
        if cache_key not in self.cache:
            return False
        
        timestamp, _ = self.cache[cache_key]
        return datetime.now() - timestamp < self.cache_timeout

    async def search_ingredient_price(self, ingredient: str, region: str = 'tunisia', quantity: float = 1.0, unit: str = 'kg') -> Optional[Dict]:
        """
        Search for real ingredient prices from multiple sources
        """
        cache_key = self.get_cache_key(ingredient, region)
        
        # Check cache first
        if self.is_cache_valid(cache_key):
            logger.info(f"Cache hit for {ingredient} in {region}")
            _, data = self.cache[cache_key]
            return data

        try:
            # Search for ingredient using multiple name variations
            search_terms = self.ingredient_mapping.get(ingredient.lower(), [ingredient])
            
            for term in search_terms:
                price_data = await self._search_openfoodfacts(term, region)
                if price_data:
                    # Adjust price based on quantity and unit
                    adjusted_price = self._adjust_price_by_quantity(price_data, quantity, unit)
                    
                    # Cache the result
                    self.cache[cache_key] = (datetime.now(), adjusted_price)
                    return adjusted_price

            # If no specific ingredient found, use market average
            market_price = await self._get_market_average(ingredient, region, quantity, unit)
            if market_price:
                self.cache[cache_key] = (datetime.now(), market_price)
                return market_price

        except Exception as e:
            logger.error(f"Error searching price for {ingredient}: {e}")

        return None

    async def _search_openfoodfacts(self, ingredient: str, region: str) -> Optional[Dict]:
        """Search OpenFoodFacts API for ingredient pricing"""
        try:
            config = self.api_configs.get(region, self.api_configs['global'])
            
            async with self.session.get(
                config['primary']['url'],
                params={**config['primary']['params'], 'search_terms': ingredient},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('products'):
                        # Find the most relevant product with price data
                        for product in data['products']:
                            if 'price' in product and product['price']:
                                return {
                                    'source': 'openfoodfacts',
                                    'price': float(product['price']),
                                    'currency': 'TND',  # Default to TND for Tunisia
                                    'quantity': product.get('quantity', '100g'),
                                    'product_name': product.get('product_name', ingredient)
                                }
                
                # Try backup API if primary fails
                if 'backup' in config:
                    return await self._search_backup_api(ingredient, config['backup'])
                    
        except Exception as e:
            logger.warning(f"OpenFoodFacts search failed for {ingredient}: {e}")
        
        return None

    async def _search_backup_api(self, ingredient: str, config: Dict) -> Optional[Dict]:
        """Search backup API"""
        try:
            async with self.session.get(
                config['url'],
                params={**config['params'], 'search_terms': ingredient},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Similar parsing logic as primary API
                    if data.get('products'):
                        for product in data['products']:
                            if 'price' in product and product['price']:
                                return {
                                    'source': 'backup_api',
                                    'price': float(product['price']),
                                    'currency': 'TND',
                                    'quantity': product.get('quantity', '100g'),
                                    'product_name': product.get('product_name', ingredient)
                                }
        except Exception as e:
            logger.warning(f"Backup API search failed for {ingredient}: {e}")
        
        return None

    async def _get_market_average(self, ingredient: str, region: str, quantity: float, unit: str) -> Optional[Dict]:
        """Get market average price for ingredient"""
        # Market average prices for common ingredients in Tunisia (TND per kg)
        market_prices = {
            'sea bass': 45.0,  # TND per kg
            'octopus': 35.0,
            'saffron': 8.5,  # per gram
            'lemon': 3.5,
            'citrus': 3.0,
            'herb oil': 25.0,
            'microgreens': 12.0,
            'risotto rice': 8.5,
            'fennel': 4.5,
            'almond': 18.0,
            'semifreddo base': 15.0
        }
        
        base_price = market_prices.get(ingredient.lower())
        if base_price:
            # Adjust for quantity and unit
            if unit == 'g' or unit == 'gram':
                adjusted_price = (base_price / 1000) * quantity
            elif unit == 'L' or unit == 'liter':
                # Assume liquid ingredients are similar density to water
                adjusted_price = base_price * quantity
            else:  # kg default
                adjusted_price = base_price * quantity
            
            return {
                'source': 'market_average',
                'price': round(adjusted_price, 2),
                'currency': 'TND',
                'quantity': f"{quantity}{unit}",
                'product_name': ingredient,
                'market_reference': True
            }
        
        return None

    def _adjust_price_by_quantity(self, price_data: Dict, quantity: float, unit: str) -> Dict:
        """Adjust price based on requested quantity and unit"""
        base_price = price_data['price']
        base_quantity = price_data.get('quantity', '100g')
        
        # Parse base quantity
        base_amount, base_unit = self._parse_quantity(base_quantity)
        
        # Convert to common unit (kg for solids, L for liquids)
        if base_unit in ['g', 'gram'] and unit in ['kg', 'kilogram']:
            adjusted_price = (base_price / base_amount) * (quantity * 1000)
        elif base_unit in ['kg', 'kilogram'] and unit in ['g', 'gram']:
            adjusted_price = (base_price / base_amount) * (quantity / 1000)
        elif base_unit in ['ml', 'milliliter'] and unit in ['L', 'liter']:
            adjusted_price = (base_price / base_amount) * (quantity * 1000)
        elif base_unit in ['L', 'liter'] and unit in ['ml', 'milliliter']:
            adjusted_price = (base_price / base_amount) * (quantity / 1000)
        else:
            # Same unit or piece-based
            adjusted_price = base_price * (quantity / base_amount if base_amount > 0 else quantity)
        
        price_data['price'] = round(adjusted_price, 2)
        price_data['quantity'] = f"{quantity}{unit}"
        price_data['unit_price'] = round(adjusted_price / quantity if quantity > 0 else adjusted_price, 2)
        
        return price_data

    def _parse_quantity(self, quantity_str: str) -> Tuple[float, str]:
        """Parse quantity string into amount and unit"""
        import re
        match = re.match(r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)', quantity_str)
        if match:
            return float(match.group(1)), match.group(2).lower()
        return 100, 'g'  # Default to 100g

    async def calculate_menu_costs(self, menu_items: List[Dict], region: str = 'tunisia') -> Dict:
        """
        Calculate total menu costs with real pricing data
        """
        total_cost = 0
        detailed_costs = []
        
        for item in menu_items:
            ingredient_costs = []
            item_total = 0
            
            for ingredient in item.get('ingredients', []):
                # Handle both string and object formats
                if isinstance(ingredient, str):
                    ingredient_name = ingredient.lower()
                    quantity = 1.0
                    unit = 'kg'
                    estimated_cost_tnd = 0
                else:
                    ingredient_name = ingredient.get('item', '').lower()
                    quantity = float(ingredient.get('quantity', 0))
                    unit = ingredient.get('unit', 'kg')
                    estimated_cost_tnd = float(ingredient.get('estimated_cost_tnd', 0))
                
                # Get real price for ingredient
                price_data = await self.search_ingredient_price(ingredient_name, region, quantity, unit)
                
                if price_data:
                    ingredient_costs.append({
                        'ingredient': ingredient_name,
                        'quantity': quantity,
                        'unit': unit,
                        'cost': price_data['price'],
                        'currency': price_data['currency'],
                        'source': price_data['source']
                    })
                    item_total += price_data['price']
                else:
                    # Fallback to estimated cost if real pricing not available
                    ingredient_costs.append({
                        'ingredient': ingredient_name,
                        'quantity': quantity,
                        'unit': unit,
                        'cost': estimated_cost_tnd,
                        'currency': 'TND',
                        'source': 'estimated'
                    })
                    item_total += estimated_cost_tnd
            
            detailed_costs.append({
                'dish_name': item.get('dish_name', ''),
                'type': item.get('type', ''),
                'total_cost': round(item_total, 2),
                'ingredients': ingredient_costs
            })
            
            total_cost += item_total
        
        return {
            'total_cost': round(total_cost, 2),
            'currency': 'TND',
            'detailed_costs': detailed_costs,
            'cost_breakdown': {
                'sourcing_method': 'real_time_api',
                'region': region,
                'last_updated': datetime.now().isoformat()
            }
        }

# Global pricing service instance
pricing_service = PricingService()

async def get_real_time_pricing(ingredients: List[Dict], region: str = 'tunisia') -> Dict:
    """
    Get real-time pricing for a list of ingredients
    """
    async with pricing_service:
        return await pricing_service.calculate_menu_costs(ingredients, region)