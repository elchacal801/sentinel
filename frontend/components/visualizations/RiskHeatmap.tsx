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
  const [selectedAsset, setSelectedAsset] = useState<RiskData | null>(null)

  useEffect(() => {
    fetchRiskData()
  }, [])

  const fetchRiskData = async () => {
    // Mock data for demo
    const mockData: RiskData[] = [
      { asset_id: '1', asset_name: 'web-prod-01', criticality: 'critical', risk_score: 9.3, critical_vulns: 3, high_vulns: 5, category: 'web_server' },
      { asset_id: '2', asset_name: 'api-gateway', criticality: 'high', risk_score: 8.7, critical_vulns: 2, high_vulns: 4, category: 'api' },
      { asset_id: '3', asset_name: 'database-01', criticality: 'critical', risk_score: 8.1, critical_vulns: 1, high_vulns: 6, category: 'database' },
      { asset_id: '4', asset_name: 'web-prod-02', criticality: 'high', risk_score: 7.8, critical_vulns: 1, high_vulns: 5, category: 'web_server' },
      { asset_id: '5', asset_name: 'app-server-01', criticality: 'high', risk_score: 7.2, critical_vulns: 0, high_vulns: 7, category: 'app_server' },
      { asset_id: '6', asset_name: 'file-server-01', criticality: 'medium', risk_score: 6.5, critical_vulns: 0, high_vulns: 4, category: 'file_server' },
      { asset_id: '7', asset_name: 'vpn-gateway', criticality: 'high', risk_score: 6.2, critical_vulns: 0, high_vulns: 3, category: 'network' },
      { asset_id: '8', asset_name: 'web-dev-01', criticality: 'medium', risk_score: 5.8, critical_vulns: 0, high_vulns: 2, category: 'web_server' },
      { asset_id: '9', asset_name: 'test-server', criticality: 'low', risk_score: 4.5, critical_vulns: 0, high_vulns: 1, category: 'app_server' },
      { asset_id: '10', asset_name: 'monitoring-01', criticality: 'medium', risk_score: 4.2, critical_vulns: 0, high_vulns: 2, category: 'monitoring' },
    ]
    setRiskData(mockData)
    setLoading(false)
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
