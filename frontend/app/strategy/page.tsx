'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Sparkles, TrendingUp, Zap } from 'lucide-react'
import { simulateStrategies } from '@/lib/api'
import { useOrg } from '@/lib/org-context'

export default function Strategy() {
  const { orgId } = useOrg();
  const [strategies, setStrategies] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleSimulate = async () => {
    setLoading(true)
    try {
      const data = await simulateStrategies(orgId)
      setStrategies(data)
    } catch (error) {
      console.error('Simulation failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Improvement Strategies</h1>
        <p className="text-muted-foreground">
          See AI-generated suggestions to improve your business health score
        </p>
      </div>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Generate Strategies</CardTitle>
          <CardDescription>
            Click below to get personalised improvement suggestions based on your data
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            onClick={handleSimulate}
            disabled={loading}
            className="w-full"
          >
            <Sparkles className="mr-2 h-4 w-4" />
            {loading ? 'Simulating...' : 'Simulate Strategies'}
          </Button>
        </CardContent>
      </Card>
      
      {strategies && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Current Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Current NSI</span>
                <Badge variant="outline" className="text-lg">
                  {strategies.current_nsi}
                </Badge>
              </div>
            </CardContent>
          </Card>
          
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Recommended Strategies</h2>
            {(strategies.strategies || strategies.options || []).map((option: any, idx: number) => (
              <Card key={idx}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="mb-2">{option.description || option.title}</CardTitle>
                      {option.reasoning && (
                        <CardDescription>{option.reasoning}</CardDescription>
                      )}
                    </div>
                    {(option.automation_eligibility || option.automatable) && (
                      <Badge className="bg-green-600">
                        <Zap className="mr-1 h-3 w-3" />
                        Automatable
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="h-4 w-4 text-green-600" />
                        <span className="text-sm font-medium">Predicted Improvement</span>
                      </div>
                      <p className="text-2xl font-bold text-green-600">
                        +{option.predicted_nsi_improvement?.toFixed?.(1) ?? option.predicted_nsi_improvement}
                      </p>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-medium">Confidence</span>
                      </div>
                      <p className="text-2xl font-bold">
                        {((option.confidence_score ?? option.confidence ?? 0) * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Confidence</span>
                      <span className="text-sm text-muted-foreground">
                        {((option.confidence_score ?? option.confidence ?? 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                    <Progress value={(option.confidence_score ?? option.confidence ?? 0) * 100} />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
