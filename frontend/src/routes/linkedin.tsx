import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Alert, AlertDescription } from '@/components/ui/alert'

export const Route = createFileRoute('/linkedin')({
  component: LinkedInPage,
})

const API_BASE = 'http://localhost:5000/api/linkedin'

interface CompetitorActivity {
  competitor_name: string
  activity_type: string
  title: string
  description: string
  signal_strength: string
  our_response: string
  source_url?: string
}

interface MarketSignal {
  signal: string
  explanation: string
  implications: string
}

interface RawPost {
  competitor_name?: string
  source?: string
  summary: string
  url?: string
}

interface LinkedInData {
  scraped_at?: string
  competitor_activities: CompetitorActivity[]
  market_signals: MarketSignal[]
  summary: string
  raw_posts: RawPost[]
  total_posts?: number
}

function LinkedInPage() {
  const [data, setData] = useState<LinkedInData | null>(null)
  const [loading, setLoading] = useState(false)
  const [scraping, setScraping] = useState(false)
  const [lastScraped, setLastScraped] = useState<string | null>(null)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    checkStatusAndLoad()
  }, [])

  const checkStatusAndLoad = async () => {
    try {
      const res = await fetch(`${API_BASE}/status`)
      const status = await res.json()
      
      if (status.has_data) {
        setLastScraped(status.last_scraped)
        await loadIntel()
      } else {
        setLastScraped(null)
      }
    } catch (err) {
      console.error('Status check error:', err)
    }
  }

  const loadIntel = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/intel`)
      
      if (res.status === 404) {
        setData(null)
        return
      }
      
      const result = await res.json()
      setData(result)
    } catch (err) {
      console.error('Load intel error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleScrape = async () => {
    setScraping(true)
    try {
      await fetch(`${API_BASE}/scrape`)
      
      const interval = setInterval(async () => {
        const res = await fetch(`${API_BASE}/status`)
        const status = await res.json()
        
        const today = new Date().toISOString().split('T')[0]
        if (status.has_data && status.last_scraped === today) {
          clearInterval(interval)
          setScraping(false)
          await loadIntel()
        }
      }, 30000)
      
      setTimeout(() => {
        clearInterval(interval)
        setScraping(false)
      }, 300000)
    } catch (err) {
      console.error('Scrape trigger error:', err)
      setScraping(false)
    }
  }

  const filteredActivities = data?.competitor_activities.filter(
    act => filter === 'all' || act.activity_type === filter
  ) || []

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-start justify-between pb-5 border-b">
        <div>
          <h1 className="text-2xl font-semibold">LinkedIn Intelligence</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Competitor activity tracked from LinkedIn company pages
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted-foreground">
            {lastScraped ? `Last scraped: ${lastScraped}` : 'Never scraped'}
          </span>
          <Button onClick={handleScrape} disabled={scraping}>
            {scraping ? 'Scraping...' : 'Scrape LinkedIn'}
          </Button>
        </div>
      </div>

      {scraping && (
        <Alert>
          <AlertDescription>
            LinkedIn scrape in progress. This takes 3-5 minutes. Page will update automatically.
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground">Intelligence Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-relaxed">
            {data?.summary || 'No data yet. Click Scrape LinkedIn to begin.'}
          </p>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Competitor Activities</h2>
          <div className="flex gap-2">
            {['all', 'product_launch', 'partnership', 'hiring', 'event'].map(f => (
              <Button
                key={f}
                variant={filter === f ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter(f)}
              >
                {f === 'all' ? 'All' : f.replace('_', ' ')}
              </Button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredActivities.length === 0 ? (
            <p className="text-sm text-muted-foreground col-span-full">
              No competitor activities found.
            </p>
          ) : (
            filteredActivities.map((act, i) => (
              <Card key={i} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between mb-2">
                    <CardTitle className="text-sm">{act.competitor_name}</CardTitle>
                    <Badge variant="secondary" className="text-xs">
                      {act.activity_type.replace('_', ' ')}
                    </Badge>
                  </div>
                  <CardDescription className="font-medium text-foreground">
                    {act.title}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {act.description}
                  </p>
                  <div className="bg-blue-50 border-l-4 border-blue-500 p-2 rounded">
                    <p className="text-xs text-blue-900 leading-relaxed">
                      {act.our_response}
                    </p>
                  </div>
                  {act.source_url && (
                    <a
                      href={act.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-primary hover:underline block"
                    >
                      View post
                    </a>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Market Signals</h2>
        <div className="space-y-3">
          {data?.market_signals.length === 0 ? (
            <p className="text-sm text-muted-foreground">No market signals detected.</p>
          ) : (
            data?.market_signals.map((sig, i) => (
              <Card key={i}>
                <CardHeader>
                  <CardTitle className="text-sm">{sig.signal}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-sm text-muted-foreground">{sig.explanation}</p>
                  <p className="text-xs text-muted-foreground italic">
                    Implication: {sig.implications}
                  </p>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Raw LinkedIn Posts</h2>
          <Badge variant="secondary">{data?.raw_posts.length || 0} posts</Badge>
        </div>
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Company</TableHead>
                <TableHead>Post Preview</TableHead>
                <TableHead>Source</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.raw_posts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} className="text-center text-muted-foreground">
                    No posts collected.
                  </TableCell>
                </TableRow>
              ) : (
                data?.raw_posts.map((post, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium whitespace-nowrap">
                      {post.competitor_name || post.source}
                    </TableCell>
                    <TableCell className="max-w-md truncate">
                      {post.summary}
                    </TableCell>
                    <TableCell>
                      {post.url ? (
                        <a
                          href={post.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-primary hover:underline"
                        >
                          View
                        </a>
                      ) : (
                        'N/A'
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </Card>
      </div>
    </div>
  )
}
