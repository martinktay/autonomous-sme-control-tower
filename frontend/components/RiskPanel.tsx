interface RiskPanelProps {
  risks: string[]
  loading?: boolean
}

export default function RiskPanel({ risks, loading }: RiskPanelProps) {
  return (
    <div className="p-6 border rounded-lg bg-white shadow-sm">
      <h2 className="text-lg font-semibold mb-4">Top Risks</h2>
      
      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : risks.length === 0 ? (
        <p className="text-gray-600">No risks identified</p>
      ) : (
        <ul className="space-y-2">
          {risks.map((risk, idx) => (
            <li key={idx} className="flex items-start">
              <span className="text-red-500 mr-2">⚠</span>
              <span className="text-gray-700">{risk}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
