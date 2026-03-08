'use client'

import { useState } from 'react'
import axios from 'axios'

export default function Memory() {
  const [query, setQuery] = useState('')
  const [orgId, setOrgId] = useState('demo-org')
  const [results, setResults] = useState<any[]>([])
  const [searching, setSearching] = useState(false)

  const handleSearch = async () => {
    setSearching(true)
    try {
      const response = await axios.post(
        'http://localhost:8000/api/memory/search',
        { query, org_id: orgId, limit: 10 }
      )
      setResults(response.data.results || [])
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-8">Memory Search</h1>
      
      <div className="max-w-2xl mb-6">
        <div className="mb-4">
          <label className="block mb-2">Organization ID</label>
          <input
            type="text"
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        
        <div className="mb-4">
          <label className="block mb-2">Search Query</label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="w-full p-2 border rounded"
            placeholder="Search operational history..."
          />
        </div>
        
        <button
          onClick={handleSearch}
          disabled={!query || searching}
          className="px-6 py-2 bg-blue-600 text-white rounded disabled:bg-gray-400"
        >
          {searching ? 'Searching...' : 'Search'}
        </button>
      </div>
      
      {results.length > 0 ? (
        <div className="space-y-4">
          {results.map((result, idx) => (
            <div key={idx} className="p-4 border rounded-lg">
              <p>{JSON.stringify(result)}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-600">No results found</p>
      )}
    </div>
  )
}
