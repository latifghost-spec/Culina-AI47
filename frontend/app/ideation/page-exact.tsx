'use client'

import { useState } from 'react'
import { ChefHat, Play, Square, RotateCcw, Download, Lightbulb, TrendingUp, DollarSign, Heart, AlertTriangle, Brain } from 'lucide-react'

export default function ChefIdeationInterface() {
  const [prompt, setPrompt] = useState('salmon and mac n cheese for dating')
  const [serving, setServing] = useState('2')
  const [dietaryTags, setDietaryTags] = useState('gluten-free')
  const [allergens, setAllergens] = useState('peanut')
  const [isStreaming, setIsStreaming] = useState(false)
  const [isLLMProcessing, setIsLLMProcessing] = useState(false)
  const [liveData, setLiveData] = useState<{
    nutrition: Array<{name: string, value: number, unit: string}>,
    cost: Array<{item: string, cost: number, quantity: string}>,
    status: string
  }>({
    nutrition: [],
    cost: [],
    status: 'Ready to start...'
  })
  const [inspiration, setInspiration] = useState('')

  const handleStreamIdeation = async () => {
    setIsStreaming(true)
    setLiveData({ nutrition: [], cost: [], status: 'Initializing stream...' })
    
    // Simulate streaming data
    const nutritionData = [
      { name: 'Calories', value: 0, unit: 'kcal' },
      { name: 'Protein', value: 0, unit: 'g' },
      { name: 'Carbs', value: 0, unit: 'g' },
      { name: 'Fat', value: 0, unit: 'g' },
      { name: 'Fiber', value: 0, unit: 'g' }
    ]
    
    const costData = [
      { item: 'Salmon', cost: 0, quantity: '0g' },
      { item: 'Macaroni', cost: 0, quantity: '0g' },
      { item: 'Cheese', cost: 0, quantity: '0g' },
      { item: 'Butter', cost: 0, quantity: '0g' },
      { item: 'Milk', cost: 0, quantity: '0ml' }
    ]

    // Simulate real-time streaming
    for (let i = 0; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Update nutrition values
      nutritionData.forEach(item => {
        item.value = Math.round((i / 100) * (Math.random() * 200 + 100))
      })
      
      // Update cost values
      costData.forEach(item => {
        item.cost = Math.round((i / 100) * (Math.random() * 15 + 5) * 100) / 100
        item.quantity = Math.round((i / 100) * (Math.random() * 200 + 50)) + 'g'
        if (item.item === 'Milk') item.quantity = Math.round((i / 100) * (Math.random() * 200 + 50)) + 'ml'
      })
      
      setLiveData({
        nutrition: [...nutritionData],
        cost: [...costData],
        status: `Streaming... ${i}%`
      })
    }
    
    setLiveData(prev => ({ ...prev, status: 'Stream complete!' }))
    setIsStreaming(false)
    
    // Generate inspiration
    setInspiration(`Based on your "${prompt}" request, consider adding fresh herbs like dill or chives to complement the salmon. The creamy mac n cheese pairs perfectly with a crisp white wine.`)
  }

  const handleLLMIdeation = async () => {
    setIsLLMProcessing(true)
    setLiveData({ nutrition: [], cost: [], status: 'Processing with AI...' })
    
    // Simulate LLM processing
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // Generate comprehensive data
    const nutritionData = [
      { name: 'Calories', value: 485, unit: 'kcal' },
      { name: 'Protein', value: 32, unit: 'g' },
      { name: 'Carbs', value: 28, unit: 'g' },
      { name: 'Fat', value: 24, unit: 'g' },
      { name: 'Fiber', value: 2, unit: 'g' }
    ]
    
    const costData = [
      { item: 'Salmon', cost: 12.50, quantity: '150g' },
      { item: 'Macaroni', cost: 1.20, quantity: '80g' },
      { item: 'Cheese', cost: 3.80, quantity: '100g' },
      { item: 'Butter', cost: 0.80, quantity: '30g' },
      { item: 'Milk', cost: 0.90, quantity: '200ml' }
    ]
    
    setLiveData({
      nutrition: nutritionData,
      cost: costData,
      status: 'AI analysis complete!'
    })
    
    setIsLLMProcessing(false)
    
    // Generate detailed inspiration
    setInspiration(`AI Analysis Complete! For your romantic dinner, this salmon mac n cheese provides excellent nutrition with 32g protein. Total cost: $19.20 for 2 servings ($9.60 per serving). Consider pairing with a crisp Sauvignon Blanc and garnish with fresh dill.`)
  }

  const handleStop = () => {
    setIsStreaming(false)
    setIsLLMProcessing(false)
    setLiveData(prev => ({ ...prev, status: 'Stopped' }))
  }

  const handleReset = () => {
    setIsStreaming(false)
    setIsLLMProcessing(false)
    setLiveData({ nutrition: [], cost: [], status: 'Ready to start...' })
    setInspiration('')
  }

  const handleDownload = () => {
    const data = {
      prompt,
      serving,
      dietaryTags,
      allergens,
      nutrition: liveData.nutrition,
      cost: liveData.cost,
      timestamp: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `culinaai-analysis-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* Header */}
      <div className="bg-black/50 backdrop-blur-lg border-b border-cyan-500/30 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <ChefHat className="w-8 h-8 text-cyan-400" />
            <h1 className="text-2xl font-bold text-white">Chef Ideation</h1>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleReset}
              className="flex items-center space-x-2 px-3 py-2 text-gray-300 hover:text-white border border-gray-600 rounded-lg hover:bg-gray-800 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reset</span>
            </button>
            <button
              onClick={handleDownload}
              disabled={liveData.nutrition.length === 0}
              className="flex items-center space-x-2 px-3 py-2 text-white bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-all duration-300"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          </div>
        </div>
      </div>

      <div className="flex h-screen">
        {/* Left Panel - Form */}
        <div className="w-1/3 bg-black/30 backdrop-blur-lg border-r border-cyan-500/30 p-6 overflow-y-auto">
          <div className="space-y-6">
            {/* Prompt Input */}
            <div>
              <label className="block text-sm font-medium text-cyan-400 mb-2">
                Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 text-white placeholder-gray-400 resize-none"
                rows={3}
                placeholder="Describe your dish idea..."
              />
            </div>

            {/* Form Controls Row */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-cyan-400 mb-2">
                  Serving
                </label>
                <input
                  type="number"
                  value={serving}
                  onChange={(e) => setServing(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 text-white placeholder-gray-400"
                  min="1"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-cyan-400 mb-2">
                  Dietary tags
                </label>
                <input
                  type="text"
                  value={dietaryTags}
                  onChange={(e) => setDietaryTags(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 text-white placeholder-gray-400"
                  placeholder="e.g., gluten-free, vegan"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-cyan-400 mb-2">
                  Allergens
                </label>
                <input
                  type="text"
                  value={allergens}
                  onChange={(e) => setAllergens(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 text-white placeholder-gray-400"
                  placeholder="e.g., nuts, dairy"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button
                onClick={handleStreamIdeation}
                disabled={isStreaming || isLLMProcessing}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:from-gray-600 disabled:to-gray-700 text-white rounded-lg font-medium transition-all duration-300 shadow-lg hover:shadow-green-500/25"
              >
                <Play className="w-4 h-4" />
                <span>Ideate (Stream)</span>
              </button>
              
              <button
                onClick={handleLLMIdeation}
                disabled={isStreaming || isLLMProcessing}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-700 text-white rounded-lg font-medium transition-all duration-300 shadow-lg hover:shadow-cyan-500/25"
              >
                <Brain className="w-4 h-4" />
                <span>Ideate (LLM)</span>
              </button>
            </div>

            {(isStreaming || isLLMProcessing) && (
              <button
                onClick={handleStop}
                className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white rounded-lg font-medium transition-all duration-300 shadow-lg hover:shadow-red-500/25"
              >
                <Square className="w-4 h-4" />
                <span>Stop</span>
              </button>
            )}

            {/* Status */}
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-600 rounded-lg p-3">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  isStreaming ? 'bg-green-500 animate-pulse' : 
                  isLLMProcessing ? 'bg-cyan-500 animate-pulse' : 
                  'bg-gray-500'
                }`} />
                <span className="text-sm text-gray-300">{liveData.status}</span>
              </div>
            </div>

            {/* Inspiration Section */}
            {inspiration && (
              <div className="bg-gradient-to-r from-yellow-900/30 to-orange-900/30 border border-yellow-500/30 rounded-lg p-4 backdrop-blur-sm">
                <div className="flex items-center space-x-2 mb-2">
                  <Lightbulb className="w-4 h-4 text-yellow-400" />
                  <h3 className="text-sm font-medium text-yellow-300">Inspiration</h3>
                </div>
                <p className="text-sm text-yellow-200">{inspiration}</p>
              </div>
            )}
          </div>
        </div>

        {/* Center/Right Panel - Live Stream */}
        <div className="flex-1 bg-gradient-to-br from-gray-900 to-black p-6 overflow-y-auto">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center space-x-2 neon-glow">
            <TrendingUp className="w-6 h-6 text-cyan-400" />
            <span>Live Nutrition/Cost Stream</span>
          </h2>

          <div className="space-y-6">
            {/* Nutrition Section */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <Heart className="w-5 h-5 text-cyan-400" />
                <span>Nutrition Analysis</span>
              </h3>
              
              {liveData.nutrition.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {liveData.nutrition.map((item, index) => (
                    <div key={index} className="bg-gradient-to-br from-gray-700 to-gray-800 rounded-lg p-4 border border-gray-600 hover:border-cyan-500/50 transition-all duration-300">
                      <div className="text-sm text-cyan-300 font-medium">{item.name}</div>
                      <div className="text-2xl font-bold text-white neon-glow">
                        {item.value} {item.unit}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-black/50 backdrop-blur-sm border border-gray-700 rounded-lg p-8 text-center">
                  <div className="text-gray-400 text-lg">Nutrition data will appear here...</div>
                </div>
              )}
            </div>

            {/* Cost Section */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <DollarSign className="w-5 h-5 text-green-400" />
                <span>Cost Analysis</span>
              </h3>
              
              {liveData.cost.length > 0 ? (
                <div className="space-y-3">
                  {liveData.cost.map((item, index) => (
                    <div key={index} className="flex items-center justify-between bg-gradient-to-r from-gray-700 to-gray-800 rounded-lg p-4 border border-gray-600 hover:border-green-500/50 transition-all duration-300">
                      <div>
                        <div className="font-medium text-white text-lg">{item.item}</div>
                        <div className="text-sm text-gray-300">{item.quantity}</div>
                      </div>
                      <div className="text-xl font-bold text-green-400 neon-glow">
                        ${item.cost.toFixed(2)}
                      </div>
                    </div>
                  ))}
                  <div className="border-t border-gray-600 pt-3 mt-3">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold text-white text-lg">Total Cost</div>
                      <div className="text-2xl font-bold text-green-400 neon-glow">
                        ${liveData.cost.reduce((sum, item) => sum + item.cost, 0).toFixed(2)}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-black/50 backdrop-blur-sm border border-gray-700 rounded-lg p-8 text-center">
                  <div className="text-gray-400 text-lg">Cost data will appear here...</div>
                </div>
              )}
            </div>

            {/* Warnings for Allergens */}
            {allergens && (
              <div className="bg-gradient-to-r from-red-900/40 to-rose-900/40 border border-red-500/40 rounded-lg p-4 backdrop-blur-sm">
                <div className="flex items-center space-x-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-red-400" />
                  <h3 className="text-sm font-medium text-red-300">Allergen Warning</h3>
                </div>
                <p className="text-sm text-red-200">
                  Recipe contains: {allergens}. Please ensure proper labeling and customer communication.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
