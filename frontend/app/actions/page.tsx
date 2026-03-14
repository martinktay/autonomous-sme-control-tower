'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import ActionLog from '@/components/ActionLog'
import { RefreshCw } from 'lucide-react'
import { getActions } from '@/lib/api'
import { useOrg } from '@/lib/org-context'

export default function Actions() {
  const { orgId } = useOrg();
  const [actions, setActions] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const fetchActions = async () => {
    setLoading(true)
    try {
      const data = await getActions(orgId)
      setActions(data.actions || [])
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
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Action History</h1>
        <p className="text-muted-foreground">
          See everything the system has done for your business — which actions
          were taken and whether they worked
        </p>
      </div>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Refresh</CardTitle>
          <CardDescription>Load the latest actions from the server</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={fetchActions} disabled={loading} className="w-full">
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Loading...' : 'Refresh Actions'}
          </Button>
        </CardContent>
      </Card>
      
      {actions.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">No actions executed yet</p>
          </CardContent>
        </Card>
      ) : (
        <ActionLog actions={actions} />
      )}
    </div>
  )
}
