'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Search, Brain, FileText, Inbox } from 'lucide-react'
import { searchMemory } from '@/lib/api'
import { useOrg } from '@/lib/org-context'

export default function Memory() {
  const [query, setQuery] = useState('')
  const { orgId } = useOrg();
  const [results, setResults] = useState<any[]>([])
  const [searching, setSearching] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = async () => {
    setSearching(true)
    setSearched(true)
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
    <div className="container mx-auto px-4 py-8 max-w-3xl">
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

      {results.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">{results.length} result{results.length !== 1 ? 's' : ''} found</p>
          {results.map((result, idx) => (
            <Card key={idx} className="hover:shadow-sm transition-shadow">
              <CardContent className="py-4">
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 mt-0.5">
                    <FileText className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0 space-y-2">
                    {/* Title / type */}
                    <div className="flex items-center gap-2 flex-wrap">
                      {result.signal_type && (
                        <Badge variant="outline" className="text-xs">{result.signal_type}</Badge>
                      )}
                      {result.content?.vendor_name && (
                        <span className="font-medium text-sm">{result.content.vendor_name}</span>
                      )}
                      {result.content?.subject && (
                        <span className="font-medium text-sm">{result.content.subject}</span>
                      )}
                      {result.similarity != null && (
                        <span className="text-xs text-muted-foreground ml-auto">
                          {(result.similarity * 100).toFixed(0)}% match
                        </span>
                      )}
                    </div>
                    {/* Key fields */}
                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                      {result.content?.amount != null && (
                        <span>{result.content.currency || ''} {result.content.amount.toLocaleString()}</span>
                      )}
                      {result.content?.category && <span>{result.content.category}</span>}
                      {result.content?.sender && <span>From: {result.content.sender}</span>}
                      {result.created_at && (
                        <span>{new Date(result.created_at).toLocaleDateString()}</span>
                      )}
                    </div>
                    {/* Summary or body snippet */}
                    {(result.content?.classification?.summary || result.content?.body) && (
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {result.content.classification?.summary || result.content.body}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {searched && results.length === 0 && !searching && (
        <Card>
          <CardContent className="py-12 text-center space-y-3">
            <Inbox className="h-10 w-10 mx-auto text-muted-foreground/50" />
            <h3 className="font-semibold">No results found</h3>
            <p className="text-sm text-muted-foreground max-w-md mx-auto">
              Try different keywords or upload more business data to search through.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
