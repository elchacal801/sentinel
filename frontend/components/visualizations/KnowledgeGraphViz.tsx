'use client'

import { useEffect, useRef, useState } from 'react'
import { Search, ZoomIn, ZoomOut, Maximize2, Filter, AlertTriangle, Network } from 'lucide-react'

interface Node {
  id: string
  label: string
  type: 'asset' | 'vulnerability' | 'threat' | 'ioc'
  properties: any
}

interface Edge {
  source: string
  target: string
  relationship: string
}

export default function KnowledgeGraphViz({ preview = false }: { preview?: boolean }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [graphData, setGraphData] = useState<{ nodes: Node[], edges: Edge[] }>({ nodes: [], edges: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    fetchGraphData()
  }, [])

  useEffect(() => {
    if (graphData.nodes.length > 0 && containerRef.current) {
      renderGraph()
    }
  }, [graphData, filter])

  const fetchGraphData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/analysis/graph/visualize')
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`)
      }
      const data = await response.json()
      setGraphData(data)
      setError(null)
      setLoading(false)
    } catch (err) {
      console.error('Failed to fetch graph data:', err)
      setError('Unable to connect to backend API. Please ensure the backend service is running at http://localhost:8000')
      setLoading(false)
    }
  }

  const renderGraph = () => {
    if (!containerRef.current) return

    // Clear previous render
    containerRef.current.innerHTML = ''

    // Create SVG
    const width = containerRef.current.clientWidth
    const height = containerRef.current.clientHeight

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
    svg.setAttribute('width', String(width))
    svg.setAttribute('height', String(height))
    svg.style.background = 'transparent'

    // Filter nodes by type
    const nodes = filter === 'all'
      ? graphData.nodes
      : graphData.nodes.filter(n => n.type === filter)

    const edges = graphData.edges.filter(e =>
      nodes.find(n => n.id === e.source) && nodes.find(n => n.id === e.target)
    )

    // Simple force-directed layout simulation
    const positions = calculatePositions(nodes, edges, width, height)

    // Draw edges
    edges.forEach(edge => {
      const sourcePos = positions[edge.source]
      const targetPos = positions[edge.target]
      if (sourcePos && targetPos) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
        line.setAttribute('x1', String(sourcePos.x))
        line.setAttribute('y1', String(sourcePos.y))
        line.setAttribute('x2', String(targetPos.x))
        line.setAttribute('y2', String(targetPos.y))
        line.setAttribute('stroke', '#374151')
        line.setAttribute('stroke-width', '1')
        line.setAttribute('opacity', '0.5')
        svg.appendChild(line)
      }
    })

    // Draw nodes
    nodes.forEach(node => {
      const pos = positions[node.id]
      if (pos) {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
        circle.setAttribute('cx', String(pos.x))
        circle.setAttribute('cy', String(pos.y))
        circle.setAttribute('r', preview ? '6' : '8')
        circle.setAttribute('fill', getNodeColor(node.type))
        circle.setAttribute('stroke', getNodeBorder(node.type))
        circle.setAttribute('stroke-width', '2')
        circle.style.cursor = 'pointer'

        circle.addEventListener('click', () => setSelectedNode(node))
        circle.addEventListener('mouseenter', () => {
          circle.setAttribute('r', preview ? '8' : '12')
        })
        circle.addEventListener('mouseleave', () => {
          circle.setAttribute('r', preview ? '6' : '8')
        })

        svg.appendChild(circle)

        if (!preview) {
          // Add label
          const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
          text.setAttribute('x', String(pos.x))
          text.setAttribute('y', String(pos.y - 12))
          text.setAttribute('text-anchor', 'middle')
          text.setAttribute('fill', '#9ca3af')
          text.setAttribute('font-size', '10')
          text.setAttribute('font-family', 'monospace')
          text.textContent = node.label.substring(0, 20)
          svg.appendChild(text)
        }
      }
    })

    containerRef.current.appendChild(svg)
  }

  const calculatePositions = (nodes: Node[], edges: Edge[], width: number, height: number) => {
    const positions: Record<string, { x: number, y: number }> = {}

    // Simple circular layout for demo
    const centerX = width / 2
    const centerY = height / 2
    const radius = Math.min(width, height) * 0.35

    nodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / nodes.length
      positions[node.id] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      }
    })

    return positions
  }

  const getNodeColor = (type: string) => {
    const colors = {
      asset: '#10b981',
      vulnerability: '#ef4444',
      threat: '#f59e0b',
      ioc: '#8b5cf6'
    }
    return colors[type as keyof typeof colors] || '#6b7280'
  }

  const getNodeBorder = (type: string) => {
    const colors = {
      asset: '#34d399',
      vulnerability: '#fca5a5',
      threat: '#fbbf24',
      ioc: '#a78bfa'
    }
    return colors[type as keyof typeof colors] || '#9ca3af'
  }


  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyber-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400 font-mono text-sm">Loading graph data...</p>
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
            <p className="mb-2">To populate the knowledge graph:</p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Start the backend API server</li>
              <li>Run collection services (ASM, OSINT, CybInt)</li>
              <li>Ensure Neo4j is running and populated</li>
            </ol>
          </div>
        </div>
      </div>
    )
  }

  if (graphData.nodes.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center max-w-md">
          <Network className="w-16 h-16 text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-200 mb-2">No Graph Data Available</h3>
          <p className="text-sm text-gray-400 mb-4">
            The knowledge graph is empty. Run collection services to populate it with intelligence data.
          </p>
          <div className="text-xs text-gray-500 bg-gray-900 border border-gray-800 rounded p-3 text-left">
            <p className="mb-2">Run these commands:</p>
            <code className="block bg-black/50 p-2 rounded">
              python -m services.asm.scanner<br/>
              python -m services.osint.collector<br/>
              python -m services.cybint.vuln_scanner
            </code>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {!preview && (
        <div className="flex items-center gap-4 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search nodes..."
              className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:border-cyber-primary"
            />
          </div>
          <div className="flex items-center gap-2">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:border-cyber-primary"
            >
              <option value="all">All Types</option>
              <option value="asset">Assets</option>
              <option value="vulnerability">Vulnerabilities</option>
              <option value="threat">Threats</option>
              <option value="ioc">IOCs</option>
            </select>
            <button className="p-2 bg-gray-900 border border-gray-700 rounded hover:bg-gray-800">
              <ZoomIn className="w-4 h-4 text-gray-400" />
            </button>
            <button className="p-2 bg-gray-900 border border-gray-700 rounded hover:bg-gray-800">
              <ZoomOut className="w-4 h-4 text-gray-400" />
            </button>
            <button className="p-2 bg-gray-900 border border-gray-700 rounded hover:bg-gray-800">
              <Maximize2 className="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </div>
      )}

      <div className="flex-1 flex gap-4">
        <div className="flex-1 bg-gray-900/50 border border-gray-800 rounded overflow-hidden">
          <div ref={containerRef} className="w-full h-full" />
        </div>

        {!preview && selectedNode && (
          <div className="w-80 bg-gray-900/50 border border-gray-800 rounded p-4 space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-semibold text-gray-200">Node Details</h4>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-gray-400 hover:text-gray-200"
                >
                  ×
                </button>
              </div>
              <div className="space-y-2">
                <div>
                  <span className="text-xs text-gray-500">ID:</span>
                  <p className="text-sm text-gray-300 font-mono">{selectedNode.id}</p>
                </div>
                <div>
                  <span className="text-xs text-gray-500">Label:</span>
                  <p className="text-sm text-gray-300 font-mono">{selectedNode.label}</p>
                </div>
                <div>
                  <span className="text-xs text-gray-500">Type:</span>
                  <p className="text-sm text-gray-300 font-mono">{selectedNode.type}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {!preview && (
        <div className="mt-4 flex items-center gap-6 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-gray-400">Assets ({graphData.nodes.filter(n => n.type === 'asset').length})</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-gray-400">Vulnerabilities ({graphData.nodes.filter(n => n.type === 'vulnerability').length})</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-gray-400">Threats ({graphData.nodes.filter(n => n.type === 'threat').length})</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-purple-500" />
            <span className="text-gray-400">IOCs ({graphData.nodes.filter(n => n.type === 'ioc').length})</span>
          </div>
        </div>
      )}
    </div>
  )
}
