'use client'

import { useState, useEffect } from 'react'
import { Shield, Activity, AlertTriangle, TrendingUp, Network, Target, Eye, Clock } from 'lucide-react'
import KnowledgeGraphViz from '@/components/visualizations/KnowledgeGraphViz'
import AttackPathViz from '@/components/visualizations/AttackPathViz'
import ThreatTimeline from '@/components/visualizations/ThreatTimeline'
import RiskHeatmap from '@/components/visualizations/RiskHeatmap'
import IntelligenceProducts from '@/components/dashboard/IntelligenceProducts'
import MetricsGrid from '@/components/dashboard/MetricsGrid'

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Fetch from backend API
      const response = await fetch('http://localhost:8000/api/v1/products/dashboard-data')
      const data = await response.json()
      setDashboardData(data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'graph', label: 'Knowledge Graph', icon: Network },
    { id: 'attack-paths', label: 'Attack Paths', icon: Target },
    { id: 'threats', label: 'Threat Timeline', icon: AlertTriangle },
    { id: 'risk', label: 'Risk Analysis', icon: TrendingUp },
    { id: 'products', label: 'Intel Products', icon: Eye },
  ]

  return (
    <div className="min-h-screen bg-intel-bg">
      <div className="border-b border-gray-800 bg-black/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6">
          {/* Header */}
          <div className="py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="w-8 h-8 text-cyber-primary" />
              <div>
                <h1 className="text-2xl font-bold text-cyber-primary terminal-text">
                  SENTINEL INTELLIGENCE PLATFORM
                </h1>
                <p className="text-xs text-gray-400 font-mono">
                  CLASSIFICATION: UNCLASSIFIED//FOUO
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1 rounded border border-green-500/30 bg-green-500/10">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-sm font-mono text-green-400">OPERATIONAL</span>
              </div>
              <div className="flex items-center gap-2 text-gray-400 text-sm font-mono">
                <Clock className="w-4 h-4" />
                {new Date().toISOString().split('T')[0]}
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1">
            {tabs.map(tab => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors
                    ${activeTab === tab.id
                      ? 'bg-cyber-primary/20 text-cyber-primary border-t-2 border-cyber-primary'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              )
            })}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-6">
        {loading ? (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <Shield className="w-16 h-16 text-cyber-primary animate-pulse mx-auto mb-4" />
              <p className="text-gray-400 font-mono">Loading intelligence data...</p>
            </div>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <MetricsGrid data={dashboardData} />
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="intel-card p-6">
                    <h3 className="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
                      <Network className="w-5 h-5 text-cyber-primary" />
                      Knowledge Graph Overview
                    </h3>
                    <div className="h-80">
                      <KnowledgeGraphViz preview={true} />
                    </div>
                  </div>

                  <div className="intel-card p-6">
                    <h3 className="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-threat-warning" />
                      Risk Distribution
                    </h3>
                    <div className="h-80">
                      <RiskHeatmap preview={true} />
                    </div>
                  </div>
                </div>

                <div className="intel-card p-6">
                  <h3 className="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-threat-critical" />
                    Recent Threat Activity
                  </h3>
                  <ThreatTimeline preview={true} />
                </div>
              </div>
            )}

            {activeTab === 'graph' && (
              <div className="intel-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-200 flex items-center gap-2">
                    <Network className="w-6 h-6 text-cyber-primary" />
                    Knowledge Graph Visualization
                  </h2>
                  <div className="text-sm text-gray-400 font-mono">
                    Interactive 3D graph of intelligence relationships
                  </div>
                </div>
                <div className="h-[calc(100vh-16rem)]">
                  <KnowledgeGraphViz />
                </div>
              </div>
            )}

            {activeTab === 'attack-paths' && (
              <div className="intel-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-200 flex items-center gap-2">
                    <Target className="w-6 h-6 text-threat-warning" />
                    Attack Path Analysis
                  </h2>
                  <div className="text-sm text-gray-400 font-mono">
                    Potential attack vectors and exploitation chains
                  </div>
                </div>
                <div className="h-[calc(100vh-16rem)]">
                  <AttackPathViz />
                </div>
              </div>
            )}

            {activeTab === 'threats' && (
              <div className="intel-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-200 flex items-center gap-2">
                    <AlertTriangle className="w-6 h-6 text-threat-critical" />
                    Threat Intelligence Timeline
                  </h2>
                  <div className="text-sm text-gray-400 font-mono">
                    Chronological threat activity and indicators
                  </div>
                </div>
                <ThreatTimeline />
              </div>
            )}

            {activeTab === 'risk' && (
              <div className="intel-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-200 flex items-center gap-2">
                    <TrendingUp className="w-6 h-6 text-cyber-primary" />
                    Risk Analysis Dashboard
                  </h2>
                  <div className="text-sm text-gray-400 font-mono">
                    Intelligence-informed risk assessment
                  </div>
                </div>
                <div className="h-[calc(100vh-16rem)]">
                  <RiskHeatmap />
                </div>
              </div>
            )}

            {activeTab === 'products' && (
              <IntelligenceProducts />
            )}
          </>
        )}
      </div>
    </div>
  )
}
