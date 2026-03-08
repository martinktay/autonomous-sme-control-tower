import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-8">Autonomous SME Control Tower</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Link href="/dashboard" className="p-6 border rounded-lg hover:bg-gray-50">
          <h2 className="text-xl font-semibold mb-2">Dashboard</h2>
          <p className="text-gray-600">View NSI and operational status</p>
        </Link>
        
        <Link href="/upload" className="p-6 border rounded-lg hover:bg-gray-50">
          <h2 className="text-xl font-semibold mb-2">Upload</h2>
          <p className="text-gray-600">Upload invoices and documents</p>
        </Link>
        
        <Link href="/memory" className="p-6 border rounded-lg hover:bg-gray-50">
          <h2 className="text-xl font-semibold mb-2">Memory</h2>
          <p className="text-gray-600">Search operational history</p>
        </Link>
        
        <Link href="/strategy" className="p-6 border rounded-lg hover:bg-gray-50">
          <h2 className="text-xl font-semibold mb-2">Strategy</h2>
          <p className="text-gray-600">View and simulate strategies</p>
        </Link>
        
        <Link href="/actions" className="p-6 border rounded-lg hover:bg-gray-50">
          <h2 className="text-xl font-semibold mb-2">Actions</h2>
          <p className="text-gray-600">Action execution history</p>
        </Link>
        
        <Link href="/voice" className="p-6 border rounded-lg hover:bg-gray-50">
          <h2 className="text-xl font-semibold mb-2">Voice</h2>
          <p className="text-gray-600">Voice briefings</p>
        </Link>
      </div>
    </main>
  )
}
