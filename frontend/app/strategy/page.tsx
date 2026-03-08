'use client'

import { useState } from 'react'
import axios from 'axios'

export default function Strategy() {
  const [orgId, setOrgId] = useState('demo-org')
  const [strategies, setStrategies] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const simulateStrategies = async () => {
    setLoading(true)
    try {
      const response = await axios.post(
        'http://localhost:8000/api/strategy/simulate',
        { org_id: orgId }
      )
      setStrategies(response.data)
    } catch (error) {
      console.error('Simulation failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-8">Strategy Simulation</h1>
      
      <div className="mb-6">
        <label className="block mb-2">Organization ID</label>
        <input
          type="text"
          value={orgId}
          onChange={(e) => setOrgId(e.target.value)}
          className="p-2 border rounded mr-4"
        />
        <button
          onClick={simulateStrategies}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded disabled:bg-gray-400"
        >
          {loading ? 'Simulating...' : 'Simulate Strategies'}
        </button>
      </div>
      
      {strategies && (
        <div className="space-y-4">
          <div className="p-4 bg-gray-50 rounded">
            <p>Current NSI: <span className="font-bold">{strategies.current_nsi}</span></p>
          </div>
          
          {strategies.options?.map((option: any, idx: number) => (
            <div key={idx} className="p-6 border rounded-lg">
              <h3 className="text-xl font-semibold mb-2">{option.title}</h3>
              <p className="mb-4">{option.description}</p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>Predicted Improvement: {option.predicted_nsi_improvement}</div>
                <div>Confidence: {(option.confidence * 100).toFixed(0)}%</div>
                <div>Automatable: {option.automatable ? 'Yes' : 'No'}</div>
                <div>Cost: {option.cost_estimate}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
