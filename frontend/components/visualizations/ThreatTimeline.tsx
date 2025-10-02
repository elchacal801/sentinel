'use client'

import { useState, useEffect } from 'react'
import { AlertTriangle, Activity, TrendingUp, Clock } from 'lucide-react'

interface ThreatEvent {
  timestamp: string
  type: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  title: string
  description: string
  threat_actor?: string
  cve_id?: string
  affected_assets: number
}

export default function ThreatTimeline({ preview = false }: { preview?: boolean }) {
  const [events, setEvents] = useState<ThreatEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    fetchThreatEvents()
  }, [])

  const fetchThreatEvents = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/intelligence/threats/timeline')
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`)
      }
      const data = await response.json()
      setEvents(data.events || [])
      setError(null)
      setLoading(false)
    } catch (err) {
      console.error('Failed to fetch threat events:', err)
      setError('Unable to connect to backend API. Please ensure the backend service is running at http://localhost:8000')
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    const colors = {
      critical: 'bg-red-500',
      high: 'bg-orange-500',
      medium: 'bg-yellow-500',
      low: 'bg-blue-500'
    }
    return colors[severity as keyof typeof colors] || 'bg-gray-500'
  }

  const getSeverityBorder = (severity: string) => {
    const colors = {
      critical: 'border-red-500',
      high: 'border-orange-500',
      medium: 'border-yellow-500',
      low: 'border-blue-500'
    }
    return colors[severity as keyof typeof colors] || 'border-gray-500'
  }

  const getTypeIcon = (type: string) => {
    const icons = {
      active_exploitation: AlertTriangle,
      new_vulnerability: Activity,
      targeted_activity: TrendingUp,
      anomaly: Activity,
      threat_intel: Activity
    }
    return icons[type as keyof typeof icons] || Activity
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    
    if (hours < 1) return 'Just now'
    if (hours < 24) return `${hours}h ago`
    const days = Math.floor(hours / 24)
    return `${days}d ago`
  }

  const filteredEvents = filter === 'all' 
    ? events 
    : events.filter(e => e.severity === filter)

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyber-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400 font-mono text-sm">Loading threat timeline...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-200 mb-2">Backend API Unavailable</h3>
          <p className="text-sm text-gray-400 mb-4">{error}</p>
          <div className="text-xs text-gray-500 bg-gray-900 border border-gray-800 rounded p-3 text-left">
            <p className="mb-2">Threat timeline requires:</p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Backend API running</li>
              <li>Threat intelligence collected (CybInt services)</li>
              <li>Event data stored in Neo4j</li>
            </ol>
          </div>
        </div>
      </div>
    )
  }

  if (events.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center max-w-md">
          <Clock className="w-16 h-16 text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-200 mb-2">No Threat Events Found</h3>
          <p className="text-sm text-gray-400 mb-4">
            No threat events have been collected yet. Run threat intelligence collection services to populate the timeline.
          </p>
          <div className="text-xs text-gray-500 bg-gray-900 border border-gray-800 rounded p-3 text-left">
            <p className="mb-2">Run these commands:</p>
            <code className="block bg-black/50 p-2 rounded">
              python -m services.cybint.threat_collector<br/>
              python -m services.osint.collector
            </code>
          </div>
        </div>
      </div>
    )
  }

  if (preview) {
    return (
      <div className="space-y-3">
        {events.slice(0, 3).map((event, index) => {
          const Icon = getTypeIcon(event.type)
          return (
            <div
              key={index}
              className="flex items-start gap-3 p-3 bg-gray-900/50 border border-gray-800 rounded hover:bg-gray-800/50 transition-colors"
            >
              <div className={`w-8 h-8 rounded-full ${getSeverityColor(event.severity)} flex items-center justify-center flex-shrink-0`}>
                <Icon className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="text-sm font-semibold text-gray-200 truncate">{event.title}</h4>
                  <span className="text-xs text-gray-500 font-mono flex-shrink-0">
                    {formatTimestamp(event.timestamp)}
                  </span>
                </div>
                <p className="text-xs text-gray-400 line-clamp-1">{event.description}</p>
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-cyber-primary text-black'
                : 'bg-gray-800 text-gray-400 hover:text-gray-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('critical')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              filter === 'critical'
                ? 'bg-red-500 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-gray-200'
            }`}
          >
            Critical
          </button>
          <button
            onClick={() => setFilter('high')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              filter === 'high'
                ? 'bg-orange-500 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-gray-200'
            }`}
          >
            High
          </button>
          <button
            onClick={() => setFilter('medium')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              filter === 'medium'
                ? 'bg-yellow-500 text-black'
                : 'bg-gray-800 text-gray-400 hover:text-gray-200'
            }`}
          >
            Medium
          </button>
        </div>
        <div className="ml-auto text-sm text-gray-400 font-mono">
          {filteredEvents.length} events
        </div>
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-800" />

        {/* Events */}
        <div className="space-y-6">
          {filteredEvents.map((event, index) => {
            const Icon = getTypeIcon(event.type)
            return (
              <div key={index} className="relative flex gap-4">
                {/* Timeline dot */}
                <div className={`
                  relative z-10 w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0
                  ${getSeverityColor(event.severity)} border-4 border-intel-bg
                `}>
                  <Icon className="w-5 h-5 text-white" />
                </div>

                {/* Content */}
                <div className={`
                  flex-1 p-4 bg-gray-900/50 border rounded
                  ${getSeverityBorder(event.severity)}
                `}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`
                          px-2 py-0.5 rounded text-xs font-medium uppercase
                          ${getSeverityColor(event.severity)} text-white
                        `}>
                          {event.severity}
                        </span>
                        <span className="text-xs text-gray-500 font-mono">
                          {new Date(event.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <h4 className="text-lg font-semibold text-gray-200">{event.title}</h4>
                    </div>
                    <div className="text-xs text-gray-500 font-mono flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatTimestamp(event.timestamp)}
                    </div>
                  </div>

                  <p className="text-sm text-gray-400 mb-3">{event.description}</p>

                  <div className="flex items-center gap-4 text-xs">
                    {event.threat_actor && (
                      <div className="flex items-center gap-1">
                        <span className="text-gray-500">Threat Actor:</span>
                        <span className="text-red-400 font-mono">{event.threat_actor}</span>
                      </div>
                    )}
                    {event.cve_id && (
                      <div className="flex items-center gap-1">
                        <span className="text-gray-500">CVE:</span>
                        <span className="text-yellow-400 font-mono">{event.cve_id}</span>
                      </div>
                    )}
                    {event.affected_assets > 0 && (
                      <div className="flex items-center gap-1">
                        <span className="text-gray-500">Affected Assets:</span>
                        <span className="text-cyber-primary font-mono">{event.affected_assets}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
