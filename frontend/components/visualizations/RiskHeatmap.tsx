'use client'

import { useState, useEffect } from 'react'
import { TrendingUp, AlertTriangle } from 'lucide-react'

interface RiskData {
  asset_id: string
  asset_name: string
  criticality: string
  risk_score: number
  critical_vulns: number
  high_vulns: number
  category: string
}

export default function RiskHeatmap({ preview = false }: { preview?: boolean }) {
  const [riskData, setRiskData] = useState<RiskData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedAsset, setSelectedAsset] = useState<RiskData | null>(null)

  useEffect(() => {
    fetchRiskData()
  }, [])

  const fetchRiskData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/analysis/risk-scores')
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`)
      }
      const data = await response.json()
      setRiskData(data.assets || [])
      setError(null)
      setLoading(false)
    } catch (err) {
      console.error('Failed to fetch risk data:', err)
      setError('Unable to connect to backend API. Please ensure the backend service is running at http://localhost:8000')
      setLoading(false)
    }
  }

  const getRiskColor = (risk: number) => {
    if (risk >= 9) return '#dc2626'
    if (risk >= 7) return '#ea580c'
    if (risk >= 5) return '#facc15'
    if (risk >= 3) return '#3b82f6'
    return '#6b7280'
  }

  const getRiskLabel = (risk: number) => {
    if (risk >= 9) return 'CRITICAL'
    if (risk >= 7) return 'HIGH'
    if (risk >= 5) return 'MEDIUM'
    return 'LOW'
  }

  const categories = Array.from(new Set(riskData.map(d => d.category)))
  const gridData = categories.map(category => ({
    category,
    assets: riskData.filter(d => d.category === category)
  }))

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyber-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400 font-mono text-sm">Calculating risk scores...</p>
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
            <p className="mb-2">Risk analysis requires:</p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Backend API running</li>
              <li>Assets discovered and cataloged</li>
              <li>Vulnerability data collected</li>
              <li>Analytics engine calculating risk scores</li>
            </ol>
          </div>
        </div>
      </div>
    )
  }

  if (riskData.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center max-w-md">
          <TrendingUp className="w-16 h-16 text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-200 mb-2">No Risk Data Available</h3>
          <p className="text-sm text-gray-400 mb-4">
            No assets with risk scores found. Run discovery and vulnerability scanning services.
          </p>
          <div className="text-xs text-gray-500 bg-gray-900 border border-gray-800 rounded p-3 text-left">
            <p className="mb-2">Run these commands:</p>
            <code className="block bg-black/50 p-2 rounded">
              python -m services.asm.scanner<br/>
              python -m services.cybint.vuln_scanner
            </code>
          </div>
        </div>
      </div>
    )
  }

  if (preview) {
    return (
      <div className="space-y-4">
        {riskData.slice(0, 5).map((asset) => (
          <div key={asset.asset_id} className="flex items-center gap-3">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-300 font-mono">{asset.asset_name}</span>
                <span className="text-sm font-bold" style={{ color: getRiskColor(asset.risk_score) }}>
                  {asset.risk_score.toFixed(1)}
                </span>
              </div>
              <div className="h-2 bg-gray-800 rounded overflow-hidden">
                <div
                  className="h-full transition-all duration-500"
                  style={{
                    width: `${(asset.risk_score / 10) * 100}%`,
                    backgroundColor: getRiskColor(asset.risk_score)
                  }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col gap-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-red-500/10 border border-red-500/30 rounded p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-red-400 uppercase">Critical Risk</span>
            <AlertTriangle className="w-4 h-4 text-red-500" />
          </div>
          <p className="text-3xl font-bold text-red-500">
            {riskData.filter(d => d.risk_score >= 9).length}
          </p>
          <p className="text-xs text-gray-500 mt-1">Assets at critical risk</p>
        </div>

        <div className="bg-orange-500/10 border border-orange-500/30 rounded p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-orange-400 uppercase">High Risk</span>
            <AlertTriangle className="w-4 h-4 text-orange-500" />
          </div>
          <p className="text-3xl font-bold text-orange-500">
            {riskData.filter(d => d.risk_score >= 7 && d.risk_score < 9).length}
          </p>
          <p className="text-xs text-gray-500 mt-1">Assets at high risk</p>
        </div>

        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-yellow-400 uppercase">Medium Risk</span>
            <TrendingUp className="w-4 h-4 text-yellow-500" />
          </div>
          <p className="text-3xl font-bold text-yellow-500">
            {riskData.filter(d => d.risk_score >= 5 && d.risk_score < 7).length}
          </p>
          <p className="text-xs text-gray-500 mt-1">Assets at medium risk</p>
        </div>

        <div className="bg-gray-500/10 border border-gray-500/30 rounded p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400 uppercase">Low Risk</span>
            <TrendingUp className="w-4 h-4 text-gray-500" />
          </div>
          <p className="text-3xl font-bold text-gray-400">
            {riskData.filter(d => d.risk_score < 5).length}
          </p>
          <p className="text-xs text-gray-500 mt-1">Assets at low risk</p>
        </div>
      </div>

      {/* Heatmap */}
      <div className="flex-1 flex gap-6">
        <div className="flex-1 bg-gray-900/50 border border-gray-800 rounded p-6 overflow-auto">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
            Risk Heatmap by Category
          </h3>
          <div className="space-y-6">
            {gridData.map((group) => (
              <div key={group.category}>
                <h4 className="text-xs text-gray-500 uppercase mb-2 font-mono">
                  {group.category.replace('_', ' ')}
                </h4>
                <div className="grid grid-cols-5 gap-2">
                  {group.assets.map((asset) => (
                    <div
                      key={asset.asset_id}
                      onClick={() => setSelectedAsset(asset)}
                      className="aspect-square rounded cursor-pointer transition-all hover:scale-110 hover:shadow-lg relative group"
                      style={{ backgroundColor: getRiskColor(asset.risk_score) }}
                    >
                      <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <span className="text-white text-xs font-bold">
                          {asset.risk_score.toFixed(1)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Details Panel */}
        {selectedAsset && (
          <div className="w-80 bg-gray-900/50 border border-gray-800 rounded p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-200">Asset Details</h3>
              <button
                onClick={() => setSelectedAsset(null)}
                className="text-gray-400 hover:text-gray-200"
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <span className="text-xs text-gray-500">Asset Name</span>
                <p className="text-gray-200 font-mono">{selectedAsset.asset_name}</p>
              </div>

              <div>
                <span className="text-xs text-gray-500">Risk Score</span>
                <div className="flex items-end gap-2 mt-1">
                  <p
                    className="text-4xl font-bold"
                    style={{ color: getRiskColor(selectedAsset.risk_score) }}
                  >
                    {selectedAsset.risk_score.toFixed(1)}
                  </p>
                  <span
                    className="text-sm font-medium mb-2"
                    style={{ color: getRiskColor(selectedAsset.risk_score) }}
                  >
                    {getRiskLabel(selectedAsset.risk_score)}
                  </span>
                </div>
              </div>

              <div>
                <span className="text-xs text-gray-500">Criticality</span>
                <p className="text-gray-200 uppercase font-mono">{selectedAsset.criticality}</p>
              </div>

              <div className="pt-4 border-t border-gray-700 space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-400">Critical Vulnerabilities:</span>
                  <span className="text-sm font-bold text-red-500">{selectedAsset.critical_vulns}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-400">High Vulnerabilities:</span>
                  <span className="text-sm font-bold text-orange-500">{selectedAsset.high_vulns}</span>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-700">
                <button className="w-full px-4 py-2 bg-cyber-primary text-black font-medium rounded hover:bg-cyber-primary/80 transition-colors">
                  View Full Report
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-6 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: getRiskColor(9.5) }} />
          <span className="text-gray-400">Critical (9.0+)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: getRiskColor(8) }} />
          <span className="text-gray-400">High (7.0-8.9)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: getRiskColor(6) }} />
          <span className="text-gray-400">Medium (5.0-6.9)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: getRiskColor(4) }} />
          <span className="text-gray-400">Low (&lt;5.0)</span>
        </div>
      </div>
    </div>
  )
}
