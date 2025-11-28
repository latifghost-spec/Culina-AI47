"use client"

import { useEffect, useMemo, useState } from "react"
import Link from "next/link"

type SupplierProduct = {
  supplier_id: string
  supplier_name: string
  product_name: string
  grade?: string | null
  unit: string
  unit_price: number
  lead_time_days: number
}

export default function SuppliersPage() {
  const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
  const [items, setItems] = useState<SupplierProduct[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    const run = async () => {
      try {
        const res = await fetch(`${API}/suppliers/catalog`)
        const data = await res.json()
        setItems(Array.isArray(data) ? data : [])
      } catch {
        setError("Failed to load suppliers")
      } finally {
        setLoading(false)
      }
    }
    run()
  }, [API])

  const activeSuppliers = useMemo(() => {
    const names = new Set(items.map(i => i.supplier_name))
    return names.size
  }, [items])

  const pendingOrders = 7

  const monthlySpend = useMemo(() => {
    const sum = items.reduce((acc, it) => acc + (Number(it.unit_price) || 0), 0)
    return sum
  }, [items])

  const topSuppliers = useMemo(() => {
    const map = new Map<string, number>()
    for (const it of items) {
      map.set(it.supplier_name, (map.get(it.supplier_name) || 0) + (Number(it.unit_price) || 0))
    }
    return Array.from(map.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
  }, [items])

  return (
    <div className="min-h-screen bg-[#0b0f1a] text-white">
      <nav className="border-b border-white/10 bg-black/40 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <span className="text-xl font-bold">CulinaAI Dashboard</span>
          </div>
          <div className="hidden md:flex items-center space-x-6">
            <Link href="/" prefetch={false} className="text-gray-300 hover:text-white">Dashboard</Link>
            <Link href="/inventory" prefetch={false} className="text-gray-300 hover:text-white">Inventory</Link>
            <Link href="/ideation" prefetch={false} className="text-gray-300 hover:text-white">Menu Generator</Link>
            <Link href="/video" prefetch={false} className="text-gray-300 hover:text-white">Video Creator</Link>
            <Link href="/suppliers" prefetch={false} className="text-white font-semibold">Suppliers</Link>
            <Link href="/financial" prefetch={false} className="text-gray-300 hover:text-white">Finances</Link>
            <Link href="/staff" prefetch={false} className="text-gray-300 hover:text-white">Staff</Link>
            <Link href="/reports" prefetch={false} className="text-gray-300 hover:text-white">Reports</Link>
            <Link href="/ai-prompts" prefetch={false} className="text-gray-300 hover:text-white">Prompts</Link>
          </div>
          <div className="flex items-center space-x-3">
            <span className="px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-300 text-xs">Demo Chef</span>
            <button className="px-3 py-1 rounded-full bg-blue-600 text-white text-xs">Make</button>
            <button className="px-3 py-1 rounded-full bg-red-600 text-white text-xs">Logout</button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-3xl font-bold">Fournisseur Management</h1>
        <p className="text-gray-400">Manage suppliers, track orders, and optimize procurement</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="bg-[#141824] rounded-2xl p-6 border border-white/10">
            <h2 className="text-lg font-semibold mb-4">Supplier Overview</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Active Suppliers</span>
                <span className="text-blue-400 font-semibold">{activeSuppliers}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Pending Orders</span>
                <span className="text-orange-400 font-semibold">{pendingOrders}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Monthly Spend</span>
                <span className="text-green-400 font-semibold">{monthlySpend.toLocaleString(undefined, { maximumFractionDigits: 0 })} TND</span>
              </div>
            </div>
          </div>

          <div className="bg-[#141824] rounded-2xl p-6 border border-white/10">
            <h2 className="text-lg font-semibold mb-4">Top Suppliers</h2>
            <div className="space-y-3">
              {topSuppliers.map(([name, amount]) => (
                <div key={name} className="flex justify-between items-center">
                  <span>{name}</span>
                  <span className="px-3 py-1 rounded-full bg-blue-600/30 text-blue-300 text-sm">
                    {Math.round(amount).toLocaleString()} TND
                  </span>
                </div>
              ))}
              {!topSuppliers.length && (
                <p className="text-gray-400">No supplier data</p>
              )}
            </div>
          </div>

          <div className="bg-[#141824] rounded-2xl p-6 border border-white/10">
            <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <button className="w-full px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700">+ Add Supplier</button>
              <button className="w-full px-4 py-2 rounded-lg bg-gray-700">Create RFP</button>
              <button className="w-full px-4 py-2 rounded-lg bg-gray-700">Performance Analysis</button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <div className="bg-[#141824] rounded-2xl p-6 border border-white/10">
            <h2 className="text-lg font-semibold mb-4">Supplier Location</h2>
            <input className="w-full bg-[#0f1320] border border-white/10 rounded-lg px-3 py-2" placeholder="Search address or place" />
          </div>
          <div className="bg-[#141824] rounded-2xl p-6 border border-white/10">
            <h2 className="text-lg font-semibold mb-4">Selected Location</h2>
            <p className="text-gray-400">No location selected</p>
          </div>
        </div>

        {loading && (
          <div className="mt-6 text-gray-400">Loading suppliers...</div>
        )}
        {error && (
          <div className="mt-6 text-red-400">{error}</div>
        )}
      </div>
    </div>
  )
}
