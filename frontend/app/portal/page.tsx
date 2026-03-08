'use client'

import { useState } from 'react'
import axios from 'axios'

export default function Portal() {
  const [orgId, setOrgId] = useState('demo-org')
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<any>(null)

  const runClosedLoop = async () => {
    setRunning(true)
    setResult(null)
    
    try {
      const response = await axios.post(
        'http://localhost:8000/api/orchestration/run-loop',
        { org_id: orgId }
      )
      setResult(response.data)
    } catch (error: any) {
      setResult({
        status: 'error',
        message: error.response?.data?.detail || error.message
      })
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-8">Autonomous Control Portal</h1>
      
      <div className="max-w-4xl">
        <div className="mb-6 p-6 bg-blue-50 border border-blue-200 rounded-lg">
          <h2 className="text-xl font-semibold mb-2">Closed Loop Execution</h2>
          <p className="text-gray-700 mb-4">
            Run the complete autonomous cycle: Diagnose → Simulate → Execute → Evaluate
          </p>
          
          <div className="mb-4">
            <label className="block mb-2">Organization ID</label>
            <input
              type="text"
              value={orgId}
              onChange={(e) => setOrgId(e.target.value)}
              className="p-2 border rounded"
            />
          </div>
          
          <button
            onClick={runClosedLoop}
            disabled={running}
            className="px-8 py-3 bg-blue-600 text-white rounded-lg disabled:bg-gray-400 font-semibold"
          >
            {running ? 'Running Closed Loop...' : 'Run Closed Loop'}
          </button>
        </div>
        
        {result && (
          <div className="space-y-4">
            <div className="p-6 border rounded-lg">
              <h3 className="text-xl font-semibold mb-4">Execution Result</h3>
              <div className="space-y-2">
                <p><span className="font-semibold">Status:</span> {result.status}</p>
                
                {result.nsi_before !== undefined && (
                  <>
                    <p><span className="font-semibold">NSI Before:</span> {result.nsi_before.toFixed(2)}</p>
                    <p><span className="font-semibold">NSI After:</span> {result.nsi_after.toFixed(2)}</p>
                    <p><span className="font-semibold">Improvement:</span> {(result.nsi_after - result.nsi_before).toFixed(2)}</p>
                  </>
                )}
                
                {result.action && (
                  <div className="mt-4 p-4 bg-gray-50 rounded">
                    <p className="font-semibold mb-2">Action Details</p>
                    <p>Action ID: {result.action.action_id}</p>
                    <p>Status: {result.action.status}</p>
                    <p>Prediction Accuracy: {result.action.prediction_accuracy ? 
                      (result.action.prediction_accuracy * 100).toFixed(1) + '%' : 'N/A'}</p>
                  </div>
                )}
                
                {result.evaluation && (
                  <div className="mt-4 p-4 bg-gray-50 rounded">
                    <p className="font-semibold mb-2">Evaluation</p>
                    <pre className="text-sm overflow-auto">
                      {JSON.stringify(result.evaluation, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
