interface NsiCardProps {
  nsi: number | null
  trend?: string
  loading?: boolean
}

export default function NsiCard({ nsi, trend, loading }: NsiCardProps) {
  const getColor = (score: number | null) => {
    if (score === null) return 'text-gray-400'
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    if (score >= 40) return 'text-orange-600'
    return 'text-red-600'
  }

  return (
    <div className="p-6 border rounded-lg bg-white shadow-sm">
      <h2 className="text-lg font-semibold mb-4">Nova Stability Index</h2>
      
      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : (
        <>
          <div className={`text-5xl font-bold mb-2 ${getColor(nsi)}`}>
            {nsi?.toFixed(1) ?? '--'}
          </div>
          {trend && (
            <p className="text-sm text-gray-600">Trend: {trend}</p>
          )}
        </>
      )}
    </div>
  )
}
