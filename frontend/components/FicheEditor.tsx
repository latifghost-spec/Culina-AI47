import React from 'react';
import { motion } from 'framer-motion';
import { ChefHat, AlertTriangle, DollarSign, Target, TrendingUp } from 'lucide-react';

type Ingredient = { name: string; quantity_g: number };
type Nutrition = { calories: number; protein_g: number; fat_g: number; carbs_g: number };

export function FicheEditor({
  title,
  yield_servings,
  ingredients,
  steps,
  plating_notes,
  allergens,
  nutrition,
  food_cost_per_serving,
  suggested_price,
}: {
  title: string;
  yield_servings: number;
  ingredients: Ingredient[];
  steps: string[];
  plating_notes?: string;
  allergens?: string[];
  nutrition?: Nutrition;
  food_cost_per_serving?: number;
  suggested_price?: number;
}) {
  const profitMargin = suggested_price && food_cost_per_serving 
    ? ((suggested_price - food_cost_per_serving) / suggested_price * 100).toFixed(0)
    : '0';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-900/20 to-secondary-900/20 rounded-xl p-6 border border-white/10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold gradient-text font-display">{title}</h2>
          <div className="flex items-center space-x-2 bg-dark-800 px-3 py-1 rounded-full">
            <ChefHat className="w-4 h-4 text-primary-400" />
            <span className="text-sm font-medium">{yield_servings} servings</span>
          </div>
        </div>
        
        {allergens && allergens.length > 0 && (
          <div className="flex items-center space-x-2 text-amber-400 bg-amber-900/20 px-3 py-2 rounded-lg">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm font-medium">Allergens: {allergens.join(', ')}</span>
          </div>
        )}
      </div>

      {/* Ingredients */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-bold mb-4 flex items-center space-x-2">
          <div className="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
            <span className="text-white text-xs font-bold">1</span>
          </div>
          <span>Ingredients</span>
        </h3>
        <div className="grid gap-3">
          {ingredients.map((ingredient, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center justify-between p-4 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors"
            >
              <span className="font-medium">{ingredient.name}</span>
              <div className="flex items-center space-x-2">
                <span className="text-primary-400 font-semibold">{ingredient.quantity_g}g</span>
                <div className="w-2 h-2 bg-primary-400 rounded-full"></div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Steps */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-bold mb-4 flex items-center space-x-2">
          <div className="w-6 h-6 bg-secondary-500 rounded-full flex items-center justify-center">
            <span className="text-white text-xs font-bold">2</span>
          </div>
          <span>Preparation Steps</span>
        </h3>
        <div className="space-y-4">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start space-x-4 p-4 bg-dark-800 rounded-lg"
            >
              <div className="w-8 h-8 bg-secondary-500 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white text-sm font-bold">{index + 1}</span>
              </div>
              <p className="text-dark-300 leading-relaxed">{step}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Plating Notes */}
      {plating_notes && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-bold mb-4 flex items-center space-x-2">
            <div className="w-6 h-6 bg-accent-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xs font-bold">3</span>
            </div>
            <span>Plating & Presentation</span>
          </h3>
          <div className="p-4 bg-gradient-to-r from-accent-900/20 to-primary-900/20 rounded-lg border border-accent-500/20">
            <p className="text-dark-300 leading-relaxed">{plating_notes}</p>
          </div>
        </div>
      )}

      {/* Nutrition & Costing */}
      {(nutrition || food_cost_per_serving !== undefined || suggested_price !== undefined) && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Nutrition */}
          {nutrition && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center space-x-2">
                <Target className="w-5 h-5 text-accent-400" />
                <span>Nutrition per Serving</span>
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-dark-800 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-accent-400">{nutrition.calories}</div>
                  <div className="text-dark-400 text-sm">Calories</div>
                </div>
                <div className="bg-dark-800 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-primary-400">{nutrition.protein_g}g</div>
                  <div className="text-dark-400 text-sm">Protein</div>
                </div>
                <div className="bg-dark-800 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-secondary-400">{nutrition.fat_g}g</div>
                  <div className="text-dark-400 text-sm">Fat</div>
                </div>
                <div className="bg-dark-800 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-400">{nutrition.carbs_g}g</div>
                  <div className="text-dark-400 text-sm">Carbs</div>
                </div>
              </div>
            </div>
          )}

          {/* Costing */}
          {(food_cost_per_serving !== undefined || suggested_price !== undefined) && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center space-x-2">
                <DollarSign className="w-5 h-5 text-green-400" />
                <span>Cost Analysis</span>
              </h3>
              <div className="space-y-4">
                {food_cost_per_serving !== undefined && (
                  <div className="flex items-center justify-between p-3 bg-dark-800 rounded-lg">
                    <span className="text-dark-300">Food Cost</span>
                    <span className="font-bold text-green-400">${food_cost_per_serving.toFixed(2)}</span>
                  </div>
                )}
                {suggested_price !== undefined && (
                  <div className="flex items-center justify-between p-3 bg-dark-800 rounded-lg">
                    <span className="text-dark-300">Menu Price</span>
                    <span className="font-bold text-primary-400">${suggested_price.toFixed(2)}</span>
                  </div>
                )}
                <div className="flex items-center justify-between p-3 bg-gradient-to-r from-green-900/20 to-primary-900/20 rounded-lg border border-green-500/20">
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="w-4 h-4 text-green-400" />
                    <span className="font-semibold">Profit Margin</span>
                  </div>
                  <span className="font-bold text-2xl text-green-400">{profitMargin}%</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
}
