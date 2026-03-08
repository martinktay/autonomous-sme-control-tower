interface Action {
  action_id: string
  status: string
  started_at: string
  completed_at?: string
  predicted_nsi_improvement: number
  actual_improvement?: number
}

interface ActionLogProps {
  actions: Action[]
  loading?: boolean
}

export default function ActionLog({ actions, loading }: ActionLogProps) {
  return (
    <div className="p-6 border rounded-lg bg-white shadow-sm">
      <h2 className="text-lg font-semibold mb-4">Recent Actions</h2>
      
      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : actions.length === 0 ? (
        <p className="text-gray-600">No actions executed yet</p>
      ) : (
        <div className="space-y-3">
          {actions.slice(0, 5).map((action) => (
            <div key={action.action_id} className="p-3 bg-gray-50 rounded">
              <div className="flex justify-between items-start mb-1">
                <span className="text-sm font-mono">{action.action_id.slice(0, 12)}...</span>
                <span className={`text-xs px-2 py-1 rounded ${
                  action.status === 'completed' ? 'bg-green-100 text-green-800' :
                  action.status === 'failed' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {action.status}
                </span>
              </div>
              <div className="text-sm text-gray-600">
                Predicted: +{action.predicted_nsi_improvement.toFixed(1)} | 
                Actual: {action.actual_improvement ? 
                  `+${action.actual_improvement.toFixed(1)}` : 'N/A'}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
