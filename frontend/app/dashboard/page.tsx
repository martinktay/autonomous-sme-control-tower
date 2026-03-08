'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'
import NsiCard from '@/components/NsiCard'
import RiskPanel from '@/components/RiskPanel'
import ActionLog from '@/components/ActionLog'

export default function Dashboard() {
  const [orgId, setOrgId] = useState('demo-org')
  const [nsi, setNsi] = useState<number | null>(null)
  const [risks, setRisks] = useState<string[]>([])
  const [actions, setActions] = useState<any[]>([])
  const [signals, setSignals] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [orgId])

  const fetchDashboardData = async () => {
    setLoading(true)
    try {
      const [nsiRes, actionsRes, signalsRes] = await Promise.all([
        axios.get(`http://localhost:8000/api/stability/${orgId}`),
        axios.get(`http://localhost:8000/api/actions/${orgId}`),
        axios.get(`http://localhost:8000/api/signals/${orgId}`)
      ])
      
      const nsiData = nsiRes.data.nsi
      if (nsiData) {
        setNsi(nsiData.nova_stability_index)
        setRisks(nsiData.top_risks || [])
      }
      
      setActions(actionsRes.data.actions || [])
      setSignals(signalsRes.data.signals || [])
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Control Tower Dashboard</h1>
        <div>
          <label className="mr-2">Org:</label>
          <input
            type="text"
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
            className="p-2 border rounded"
          />
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <NsiCard nsi={nsi} loading={loading} />
        <RiskPanel risks={risks} loading={loading} />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ActionLog actions={actions} loading={loading} />
        
        <div className="p-6 border rounded-lg bg-white shadow-sm">
          <h2 className="text-lg font-semibold mb-4">Signals</h2>
          {loading ? (
            <p className="text-gray-500">Loading...</p>
          ) : (
            <p className="text-gray-600">{signals.length} signals processed</p>
          )}
        </div>
      </div>
    </div>
  )
}
