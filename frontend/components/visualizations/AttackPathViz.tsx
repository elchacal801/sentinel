'use client'

import { useEffect, useState } from 'react'
import { AlertTriangle, TrendingUp, Eye, Shield } from 'lucide-react'

interface AttackPath {
  rank: number
  likelihood: number
  difficulty: number
  detectability: number
  impact: number
  overall_risk: number
  skill_required: string
  estimated_time: string
  nodes: any[]
  recommendations: string[]
}

export default function AttackPathViz() {
  const [paths, setPaths] = useState<AttackPath[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedPath, setSelectedPath] = useState<AttackPath | null>(null)

  useEffect(() => {
    fetchAttackPaths()
  }, [])

  const fetchAttackPaths = async () => {
    try {
      // Mock data for demo
      const mockPaths: AttackPath[] = [
        {
          rank: 1,
          likelihood: 0.85,
          difficulty: 3.2,
          detectability: 0.35,
          impact: 9.0,
          overall_risk: 9.3,
          skill_required: 'medium',
          estimated_time: '2-4 hours',
          nodes: ['Internet', 'Web Server', 'App Server', 'Database'],
          recommendations: [
            'Implement network segmentation',
            'Deploy WAF on web server',
            'Enable MFA for database access'
          ]
        },
        {
          rank: 2,
          likelihood: 0.72,
          difficulty: 5.1,
          detectability: 0.55,
          impact: 8.5,
          overall_risk: 8.1,
          skill_required: 'high',
          estimated_time: '1-2 days',
          nodes: ['Internet', 'VPN', 'Internal Network', 'File Server'],
          recommendations: [
            'Patch VPN vulnerabilities',
            'Implement zero-trust architecture'
          ]
        },
        {
          rank: 3,
          likelihood: 0.60,
          difficulty: 4.8,
          detectability: 0.70,
          impact: 7.0,
          overall_risk: 7.2,
          skill_required: 'high',
          estimated_time: '3-5 days',
          nodes: ['Phishing Email', 'User Workstation', 'Domain Controller'],
          recommendations: [
            'Security awareness training',
            'Email filtering enhancement',
            'Privileged access management'
          ]
        }
      ]
      setPaths(mockPaths)
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch attack paths:', error)
      setLoading(false)
    }
  }

  const getRiskColor = (risk: number) => {
    if (risk >= 9) return 'text-threat-critical'
    if (risk >= 7) return 'text-threat-warning'
    if (risk >= 4) return 'text-threat-info'
    return 'text-gray-400'
  }

  const getRiskBg = (risk: number) => {
    if (risk >= 9) return 'bg-threat-critical/20 border-threat-critical/50'
    if (risk >= 7) return 'bg-threat-warning/20 border-threat-warning/50'
    if (risk >= 4) return 'bg-threat-info/20 border-threat-info/50'
    return 'bg-gray-800/20 border-gray-700/50'
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyber-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400 font-mono text-sm">Analyzing attack paths...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex gap-6">
      {/* Path List */}
      <div className="w-96 space-y-3 overflow-y-auto">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
          Identified Attack Paths ({paths.length})
        </h3>
        {paths.map(path => (
          <div
            key={path.rank}
            onClick={() => setSelectedPath(path)}
            className={`
              border rounded p-4 cursor-pointer transition-all
              ${selectedPath?.rank === path.rank
                ? 'bg-cyber-primary/10 border-cyber-primary'
                : `${getRiskBg(path.overall_risk)} hover:bg-gray-800/50`
              }
            `}
          >
            <div className="flex items-start justify-between mb-2">
              <div>
                <span className="text-xs text-gray-500">Path #{path.rank}</span>
                <h4 className={`text-lg font-bold ${getRiskColor(path.overall_risk)}`}>
                  Risk: {path.overall_risk.toFixed(1)}
                </h4>
              </div>
              <div className={`px-2 py-1 rounded text-xs font-mono ${
                path.overall_risk >= 9 ? 'bg-threat-critical text-white' :
                path.overall_risk >= 7 ? 'bg-threat-warning text-black' :
                'bg-threat-info text-white'
              }`}>
                {path.skill_required.toUpperCase()}
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Likelihood:</span>
                <span className="text-gray-200 font-mono">{(path.likelihood * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Detectability:</span>
                <span className="text-gray-200 font-mono">{(path.detectability * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Time Est.:</span>
                <span className="text-gray-200 font-mono">{path.estimated_time}</span>
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-gray-700">
              <p className="text-xs text-gray-500 mb-1">Attack Chain:</p>
              <p className="text-xs text-gray-300 font-mono">
                {path.nodes.join(' → ')}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Path Details */}
      <div className="flex-1 space-y-6">
        {selectedPath ? (
          <>
            {/* Visualization */}
            <div className="bg-gray-900/50 border border-gray-800 rounded p-6">
              <h3 className="text-lg font-semibold text-gray-200 mb-6">Attack Path Visualization</h3>
              <div className="flex items-center justify-between">
                {selectedPath.nodes.map((node, index) => (
                  <div key={index} className="flex items-center">
                    <div className="flex flex-col items-center">
                      <div className={`
                        w-16 h-16 rounded-full flex items-center justify-center border-2
                        ${index === 0 ? 'bg-red-500/20 border-red-500' :
                          index === selectedPath.nodes.length - 1 ? 'bg-purple-500/20 border-purple-500' :
                          'bg-gray-700 border-gray-600'}
                      `}>
                        {index === 0 ? <AlertTriangle className="w-6 h-6 text-red-500" /> :
                         index === selectedPath.nodes.length - 1 ? <Shield className="w-6 h-6 text-purple-500" /> :
                         <div className="w-3 h-3 rounded-full bg-gray-400" />}
                      </div>
                      <p className="mt-2 text-xs text-gray-400 text-center font-mono">{node}</p>
                    </div>
                    {index < selectedPath.nodes.length - 1 && (
                      <div className="w-16 h-0.5 bg-gradient-to-r from-gray-600 to-gray-700 mx-2" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-gray-900/50 border border-gray-800 rounded p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-4 h-4 text-red-500" />
                  <span className="text-xs text-gray-400">Likelihood</span>
                </div>
                <p className="text-2xl font-bold text-red-500">{(selectedPath.likelihood * 100).toFixed(0)}%</p>
                <p className="text-xs text-gray-500 mt-1">Success probability</p>
              </div>

              <div className="bg-gray-900/50 border border-gray-800 rounded p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="w-4 h-4 text-yellow-500" />
                  <span className="text-xs text-gray-400">Difficulty</span>
                </div>
                <p className="text-2xl font-bold text-yellow-500">{selectedPath.difficulty.toFixed(1)}/10</p>
                <p className="text-xs text-gray-500 mt-1">Skill required</p>
              </div>

              <div className="bg-gray-900/50 border border-gray-800 rounded p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Eye className="w-4 h-4 text-blue-500" />
                  <span className="text-xs text-gray-400">Detectability</span>
                </div>
                <p className="text-2xl font-bold text-blue-500">{(selectedPath.detectability * 100).toFixed(0)}%</p>
                <p className="text-xs text-gray-500 mt-1">Detection chance</p>
              </div>

              <div className="bg-gray-900/50 border border-gray-800 rounded p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-purple-500" />
                  <span className="text-xs text-gray-400">Impact</span>
                </div>
                <p className="text-2xl font-bold text-purple-500">{selectedPath.impact.toFixed(1)}/10</p>
                <p className="text-xs text-gray-500 mt-1">Damage potential</p>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-gray-900/50 border border-gray-800 rounded p-6">
              <h3 className="text-lg font-semibold text-gray-200 mb-4">Mitigation Recommendations</h3>
              <div className="space-y-3">
                {selectedPath.recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-gray-800/50 rounded border border-gray-700">
                    <div className="w-6 h-6 rounded-full bg-cyber-primary/20 flex items-center justify-center flex-shrink-0">
                      <span className="text-xs font-bold text-cyber-primary">{index + 1}</span>
                    </div>
                    <p className="text-sm text-gray-300">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500">
            <div className="text-center">
              <Shield className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="font-mono">Select an attack path to view details</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
