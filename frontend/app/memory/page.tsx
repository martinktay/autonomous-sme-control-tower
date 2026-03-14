'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search, Brain } from 'lucide-react'
import { searchMemory } from '@/lib/api'
import { useOrg } from '@/lib/org-context'

export default function Memory() {
  const [query, setQuery] = useState('')
  const { orgId } = useOrg();
  const [results, setResults] = useState<any[]>([])
  const [searching, setSearching] = useState(false)

  const handleSearch = async () => {
    setSearching(true)
    try {
      const data = await searchMemory(orgId, query, 10)
      setResults(data.results || [])
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="container mx-auto p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Search Business History</h1>
        <p className="text-muted-foreground">
          Search through your past invoices, emails, and business data using
          plain language
        </p>
      </div>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Search Your Data
          </CardTitle>
          <CardDescription>
            Type what you are looking for in everyday language, like
            &quot;overdue invoices&quot; or &quot;payments from last month&quot;
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Search Query</label>
            <Input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="e.g., overdue invoices, customer complaints..."
            />
          </div>
          
          <Button
            onClick={handleSearch}
            disabled={!query || searching}
            className="w-full"
          >
            <Search className="mr-2 h-4 w-4" />
            {searching ? 'Searching...' : 'Search Memory'}
          </Button>
        </CardContent>
      </Card>
      
      {results.length > 0 ? (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Search Results</h2>
          {results.map((result, idx) => (
            <Card key={idx}>
              <CardContent className="pt-6">
                <pre className="text-sm whitespace-pre-wrap">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : query && !searching ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">No results found</p>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
