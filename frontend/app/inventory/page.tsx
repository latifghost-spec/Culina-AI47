'use client'

export default function InventoryPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="max-w-7xl mx-auto px-6 py-10">
        <div className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Inventory</h1>
            <div className="px-3 py-1 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full text-xs font-semibold text-white">DEMO v2.0</div>
          </div>

          <p className="text-gray-300 mb-6">
            This is a demo inventory page. The full inventory management module will include stock levels,
            supplier integration, and real-time costing. For now, use the ideation page to generate recipes.
          </p>

          <div className="flex gap-4">
            <a href="/ideation" className="inline-flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-white px-4 py-2 rounded-lg shadow-lg shadow-cyan-500/25">
              <span>🧠</span>
              <span>Go to Ideation</span>
            </a>
            <a href="/" className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg border border-white/10">
              <span>🏠</span>
              <span>Back Home</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

