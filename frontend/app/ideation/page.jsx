"use client";
import React, { useState } from 'react';
import { FicheEditor } from '../../components/FicheEditor';

export default function Page() {
  const [prompt, setPrompt] = useState('salmon and matcha fine dining');
  const [servings, setServings] = useState(2);
  const [dietTags, setDietTags] = useState('gluten-free');
  const [allergens, setAllergens] = useState('peanut');
  const [buffer, setBuffer] = useState('');
  const [fiche, setFiche] = useState(null);
  const [videos, setVideos] = useState([]);
  const [liveCalc, setLiveCalc] = useState('');
  const [partialIngredients, setPartialIngredients] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState('create');

  const backend = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

  async function fetchVideos() {
    const res = await fetch(`${backend}/inspiration/videos?prompt=${encodeURIComponent(prompt)}`);
    const data = await res.json();
    setVideos(data.video_urls || []);
  }

  async function computeCostAndNutrition(f) {
    const ingredients = f.ingredients.map(i => ({ name: i.name, quantity_g: i.quantity_g }));
    const nut = await fetch(`${backend}/calc/nutrition?servings=${f.yield_servings}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(ingredients)
    });
    const nutJson = await nut.json();
    const cost = await fetch(`${backend}/calc/costing?servings=${f.yield_servings}&target_cost_pct=0.3`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(ingredients)
    });
    const costJson = await cost.json();
    setFiche({ ...f, nutrition_per_serving: nutJson.per_serving, food_cost_per_serving: costJson.food_cost_per_serving, suggested_price: costJson.suggested_price });
  }

  function ideateStream() {
    setIsGenerating(true);
    setBuffer('');
    setFiche(null);
    setLiveCalc('');
    
    const url = `${backend}/chef/ideate/stream?prompt=${encodeURIComponent(prompt)}&servings=${servings}&excluded_allergens=${encodeURIComponent(allergens)}&dietary_tags=${encodeURIComponent(dietTags)}`;
    const es = new EventSource(url);
    let acc = '';
    
    es.onmessage = (ev) => {
      acc += ev.data;
      setBuffer(prev => prev + ev.data);
      try {
        const ingredientsMatch = acc.match(/"ingredients"\s*:\s*\[[\s\S]*?\]/);
        if (ingredientsMatch) {
          const objRegex = /\{\s*"name"\s*:\s*"([^"]+)",\s*"quantity_g"\s*:\s*([0-9.]+)\s*\}/g;
          const found = [];
          let m;
          while ((m = objRegex.exec(ingredientsMatch[0])) !== null) {
            found.push({ name: m[1], quantity_g: Number(m[2]) });
          }
          if (found.length) {
            setPartialIngredients(found);
            const urlLive = `${backend}/calc/live?servings=${servings}`;
            const esLive = new EventSource(urlLive);
            esLive.onmessage = (ev) => setLiveCalc(prev => prev + ev.data + '\n');
            fetch(urlLive, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(found) }).catch(()=>{});
          }
        }
      } catch {}
    };
    
    es.addEventListener('end', async () => {
      es.close();
      setIsGenerating(false);
      try {
        const f = JSON.parse(acc.replace(/^```json\s*/,'').replace(/^```/, '').replace(/```$/, ''));
        setFiche(f);
        await computeCostAndNutrition(f);
        fetchVideos();
      } catch {}
    });
    
    es.onerror = () => {
      es.close();
      setIsGenerating(false);
    };
  }

  function liveCalcStream() {
    setLiveCalc('');
    if (!fiche) return;
    const url = `${backend}/calc/live?servings=${fiche.yield_servings}`;
    const es = new EventSource(url);
    es.onerror = () => es.close();
    es.onmessage = (ev) => setLiveCalc(prev => prev + ev.data + '\n');
    fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(fiche.ingredients.map(i => ({ name: i.name, quantity_g: i.quantity_g }))) })
      .catch(()=>{})
      .finally(()=>{});
  }

  const tabs = [
    { id: 'create', label: 'Create', icon: '🧠' },
    { id: 'nutrition', label: 'Nutrition', icon: '🎯' },
    { id: 'costing', label: 'Costing', icon: '💰' },
    { id: 'inspiration', label: 'Inspiration', icon: '✨' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="bg-black/40 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl flex items-center justify-center shadow-lg shadow-cyan-500/25">
                <span className="text-white text-2xl">🧑‍🍳</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">CulinaAI</h1>
                <p className="text-gray-400 text-sm">Professional Culinary Intelligence</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="px-3 py-1 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full text-xs font-semibold text-white shadow-lg shadow-cyan-500/25">
                DEMO v2.0
              </div>
              <a href="/" className="text-gray-300 hover:text-white transition-colors flex items-center space-x-1">
                <span>←</span>
                <span>Back to Home</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Panel - Controls */}
          <div className="lg:col-span-1">
            <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-6 shadow-2xl">
              <h2 className="text-xl font-bold mb-6 flex items-center space-x-2 text-white">
                <span className="text-2xl">🧠</span>
                <span>AI Recipe Generator</span>
              </h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-300">Dish Concept</label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    className="w-full h-24 resize-none bg-black/50 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                    placeholder="Describe your dish idea..."
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">Servings</label>
                    <input
                      type="number"
                      value={servings}
                      onChange={(e) => setServings(Number(e.target.value))}
                      className="w-full bg-black/50 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                      min="1"
                      max="20"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">Target Cost %</label>
                    <select className="w-full bg-black/50 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all" defaultValue="0.3">
                      <option value="0.25">25%</option>
                      <option value="0.3">30%</option>
                      <option value="0.35">35%</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-300">Dietary Tags</label>
                  <input
                    value={dietTags}
                    onChange={(e) => setDietTags(e.target.value)}
                    className="w-full bg-black/50 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                    placeholder="gluten-free, keto, vegan..."
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-300">Exclude Allergens</label>
                  <input
                    value={allergens}
                    onChange={(e) => setAllergens(e.target.value)}
                    className="w-full bg-black/50 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                    placeholder="peanut, shellfish, dairy..."
                  />
                </div>
                
                <button
                  onClick={ideateStream}
                  disabled={isGenerating}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 disabled:from-gray-600 disabled:to-gray-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg shadow-cyan-500/25 disabled:shadow-none"
                >
                  {isGenerating ? (
                    <>
                      <span className="animate-spin">⚡</span>
                      <span>Generating...</span>
                    </>
                  ) : (
                    <>
                      <span>✨</span>
                      <span>Generate Recipe</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Live Calculations */}
            {partialIngredients.length > 0 && (
              <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
                <h3 className="text-lg font-bold mb-4 flex items-center space-x-2 text-white">
                  <span className="text-xl">🧮</span>
                  <span>Live Calculations</span>
                </h3>
                <div className="bg-black/50 rounded-lg p-4 font-mono text-sm border border-white/10">
                  <pre className="whitespace-pre-wrap text-cyan-300">{liveCalc}</pre>
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Results */}
          <div className="lg:col-span-2">
            {/* Tab Navigation */}
            <div className="flex space-x-1 mb-6 bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-1 shadow-2xl">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 rounded-xl transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg shadow-cyan-500/25'
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span className="text-sm font-medium">{tab.label}</span>
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="space-y-6">
              {activeTab === 'create' && (
                <div className="space-y-6">
                  {/* Streaming Output */}
                  {buffer && (
                    <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
                      <h3 className="text-lg font-bold mb-4 flex items-center space-x-2 text-white">
                        <span className="text-xl">⚡</span>
                        <span>AI Generation Stream</span>
                      </h3>
                      <div className="bg-black/50 rounded-lg p-4 font-mono text-sm max-h-64 overflow-y-auto border border-white/10">
                        <pre className="whitespace-pre-wrap text-cyan-300">{buffer}</pre>
                      </div>
                    </div>
                  )}

                  {/* Fiche Editor */}
                  {fiche && (
                    <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold flex items-center space-x-2 text-white">
                          <span className="text-2xl">🏆</span>
                          <span>Fiche Technique</span>
                        </h3>
                        <button
                          onClick={liveCalcStream}
                          className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white px-4 py-2 rounded-lg text-sm transition-colors shadow-lg shadow-cyan-500/25"
                        >
                          Recalculate
                        </button>
                      </div>
                      <FicheEditor
                        title={fiche.title}
                        yield_servings={fiche.yield_servings}
                        ingredients={fiche.ingredients}
                        steps={fiche.steps}
                        plating_notes={fiche.plating_notes}
                        allergens={fiche.allergens}
                        nutrition={fiche.nutrition_per_serving}
                        food_cost_per_serving={fiche.food_cost_per_serving}
                        suggested_price={fiche.suggested_price}
                      />
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'nutrition' && fiche && (
                <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
                  <h3 className="text-xl font-bold mb-6 flex items-center space-x-2 text-white">
                    <span className="text-2xl">🎯</span>
                    <span>Nutritional Analysis</span>
                  </h3>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-black/50 rounded-lg p-6 border border-white/10">
                      <h4 className="font-semibold mb-4 text-cyan-300">Per Serving</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-300">Calories</span>
                          <span className="font-semibold text-white">{fiche.nutrition_per_serving?.calories || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Protein</span>
                          <span className="font-semibold text-white">{fiche.nutrition_per_serving?.protein_g || 0}g</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Fat</span>
                          <span className="font-semibold text-white">{fiche.nutrition_per_serving?.fat_g || 0}g</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Carbs</span>
                          <span className="font-semibold text-white">{fiche.nutrition_per_serving?.carbs_g || 0}g</span>
                        </div>
                      </div>
                    </div>
                    <div className="bg-black/50 rounded-lg p-6 border border-white/10">
                      <h4 className="font-semibold mb-4 text-cyan-300">Health Score</h4>
                      <div className="text-center">
                        <div className="text-4xl font-bold text-cyan-400 mb-2">A+</div>
                        <p className="text-gray-300 text-sm">Excellent nutritional profile</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'costing' && fiche && (
                <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
                  <h3 className="text-xl font-bold mb-6 flex items-center space-x-2 text-white">
                    <span className="text-2xl">💰</span>
                    <span>Cost Analysis</span>
                  </h3>
                  <div className="grid md:grid-cols-3 gap-6">
                    <div className="bg-black/50 rounded-lg p-6 border border-white/10">
                      <h4 className="font-semibold mb-2 text-green-300">Food Cost</h4>
                      <div className="text-3xl font-bold text-green-400">
                        ${fiche.food_cost_per_serving?.toFixed(2) || '0.00'}
                      </div>
                      <p className="text-gray-300 text-sm">per serving</p>
                    </div>
                    <div className="bg-black/50 rounded-lg p-6 border border-white/10">
                      <h4 className="font-semibold mb-2 text-blue-300">Suggested Price</h4>
                      <div className="text-3xl font-bold text-primary-400">
                        ${fiche.suggested_price?.toFixed(2) || '0.00'}
                      </div>
                      <p className="text-gray-300 text-sm">menu price</p>
                    </div>
                    <div className="bg-black/50 rounded-lg p-6 border border-white/10">
                      <h4 className="font-semibold mb-2 text-purple-300">Margin</h4>
                      <div className="text-3xl font-bold text-accent-400">
                        {fiche.suggested_price && fiche.food_cost_per_serving 
                          ? ((fiche.suggested_price - fiche.food_cost_per_serving) / fiche.suggested_price * 100).toFixed(0) + '%'
                          : '0%'}
                      </div>
                      <p className="text-gray-300 text-sm">profit margin</p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'inspiration' && (
                <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
                  <h3 className="text-xl font-bold mb-6 flex items-center space-x-2 text-white">
                    <span className="text-2xl">✨</span>
                    <span>Video Inspiration</span>
                  </h3>
                  {videos.length > 0 ? (
                    <div className="grid gap-4">
                      {videos.map((v, i) => (
                        <a
                          key={i}
                          href={v}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center space-x-4 p-4 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors"
                        >
                          <span className="text-2xl">▶</span>
                          <div className="flex-1">
                            <div className="font-semibold text-white">Inspiration Video {i + 1}</div>
                            <div className="text-gray-400 text-sm">{v}</div>
                          </div>
                          <span className="text-gray-400">→</span>
                        </a>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <div className="text-6xl text-gray-600 mx-auto mb-4">✨</div>
                      <p className="text-gray-400">Generate a recipe to see inspiration videos</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
