'use client'

import { useState } from 'react'
import axios from 'axios'

export default function Upload() {
  const [file, setFile] = useState<File | null>(null)
  const [orgId, setOrgId] = useState('demo-org')
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleUpload = async () => {
    if (!file) return
    
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      const response = await axios.post(
        `http://localhost:8000/api/invoices/upload?org_id=${orgId}`,
        formData
      )
      setResult(response.data)
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-8">Upload Invoice</h1>
      
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
        
        <div className="mb-4">
          <label className="block mb-2">Invoice File</label>
          <input
            type="file"
            accept=".pdf,image/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="w-full p-2 border rounded"
          />
        </div>
        
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="px-6 py-2 bg-blue-600 text-white rounded disabled:bg-gray-400"
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
        
        {result && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded">
            <h3 className="font-semibold mb-2">Upload Successful</h3>
            <pre className="text-sm">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  )
}
