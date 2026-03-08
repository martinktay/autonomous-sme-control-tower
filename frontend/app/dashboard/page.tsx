'use client'

import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [nsi, setNsi] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Fetch NSI from API
    setLoading(false)
  }, [])

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-8">Control Tower Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 border rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Nova Stability Index</h2>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <div className="text-5xl font-bold">{nsi ?? '--'}</div>
          )}
        </div>
        
        <div className="p-6 border rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Top Risks</h2>
          <ul className="space-y-2">
            <li className="text-gray-600">No risks identified</li>
          </ul>
        </div>
        
        <div className="p-6 border rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Recent Actions</h2>
          <p className="text-gray-600">No actions yet</p>
        </div>
        
        <div className="p-6 border rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Signals</h2>
          <p className="text-gray-600">No signals processed</p>
        </div>
      </div>
    </div>
  )
}
