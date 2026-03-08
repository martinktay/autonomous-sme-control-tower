'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'

export default function Actions() {
  const [orgId, setOrgId] = useState('demo-org')
  const [actions, setActions] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const fetchActions = async () => {
    setLoading(true)
    try {
      const response = await axios.get(
        `http://localhost:8000/api/actions/${orgId}`
      )
      setActions(response.data.actions || [])
    } catch (error) {
      console.error('Failed to fetch actions:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchActions()
  }, [orgId])

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-8">Action History</h1>
      
      <div className="mb-6">
        <label className="block mb-2">Organization ID</label>
        <input
          type="text"
          value={orgId}
          onChange={(e) => setOrgId(e.target.value)}
          className="p-2 border rounded"
        />
      </div>
      
      {loading ? (
        <p>Loading...</p>
      ) : actions.length === 0 ? (
        <p className="text-gray-600">No actions executed yet</p>
      ) : (
        <div className="space-y-4">
          {actions.map((action, idx) => (
            <div key={idx} className="p-6 border rounded-lg">
              <div className="flex justify-between mb-4">
                <h3 className="text-xl font-semibold">{action.action_id}</h3>
                <span className={`px-3 py-1 rounded text-sm ${
                  action.status === 'completed' ? 'bg-green-100 text-green-800' :
                  action.status === 'failed' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {action.status}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>Predicted Improvement: {action.predicted_nsi_improvement}</div>
                <div>Actual Improvement: {action.actual_improvement ?? 'N/A'}</div>
                <div>Started: {action.started_at}</div>
                <div>Completed: {action.completed_at ?? 'N/A'}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
