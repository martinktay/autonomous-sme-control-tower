'use client'

import { useState } from 'react'
import axios from 'axios'

export default function Voice() {
  const [orgId, setOrgId] = useState('demo-org')
  const [summary, setSummary] = useState('')
  const [loading, setLoading] = useState(false)

  const generateBrief = async () => {
    setLoading(true)
    try {
      const response = await axios.get(
        `http://localhost:8000/api/voice/${orgId}/summary`
      )
      setSummary(response.data.summary)
    } catch (error) {
      console.error('Failed to generate brief:', error)
    } finally {
      setLoading(false)
    }
  }

  const playAudio = async () => {
    try {
      const response = await axios.post(
        'http://localhost:8000/api/voice/brief',
        { org_id: orgId },
        { responseType: 'blob' }
      )
      
      const audioUrl = URL.createObjectURL(response.data)
      const audio = new Audio(audioUrl)
      audio.play()
    } catch (error) {
      console.error('Failed to play audio:', error)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-8">Voice Briefing</h1>
      
      <div className="max-w-2xl">
        <div className="mb-4">
          <label className="block mb-2">Organization ID</label>
          <input
            type="text"
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        
        <div className="space-x-4 mb-6">
          <button
            onClick={generateBrief}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded disabled:bg-gray-400"
          >
            {loading ? 'Generating...' : 'Generate Brief'}
          </button>
          
          <button
            onClick={playAudio}
            className="px-6 py-2 bg-green-600 text-white rounded"
          >
            Play Audio
          </button>
        </div>
        
        {summary && (
          <div className="p-6 border rounded-lg bg-gray-50">
            <h3 className="font-semibold mb-2">Briefing Text</h3>
            <p className="whitespace-pre-wrap">{summary}</p>
          </div>
        )}
      </div>
    </div>
  )
}
