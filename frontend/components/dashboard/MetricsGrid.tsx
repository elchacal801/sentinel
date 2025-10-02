'use client'

import { Shield, Activity, AlertTriangle, TrendingUp, Eye, Database, Network } from 'lucide-react'

interface MetricsGridProps {
  data: any
}

export default function MetricsGrid({ data }: MetricsGridProps) {
  const metrics = [
    {
      label: 'Assets Monitored',
      value: data?.metrics?.assets_monitored || '127',
      change: '+12',
      trend: 'up',
      icon: Shield,
      color: 'text-cyber-primary',
      bgColor: 'bg-cyber-primary/10',
      borderColor: 'border-cyber-primary/30'
    },
    {
      label: 'Active Threats',
      value: data?.metrics?.threats_detected || '8',
      change: '+3',
      trend: 'up',
      icon: AlertTriangle,
      color: 'text-threat-critical',
      bgColor: 'bg-threat-critical/10',
      borderColor: 'border-threat-critical/30'
    },
    {
      label: 'Critical Vulnerabilities',
      value: data?.metrics?.critical_vulnerabilities || '15',
      change: '-2',
      trend: 'down',
      icon: Activity,
      color: 'text-threat-warning',
      bgColor: 'bg-threat-warning/10',
      borderColor: 'border-threat-warning/30'
    },
    {
      label: 'Risk Score (Avg)',
      value: data?.metrics?.average_risk_score || '6.8',
      change: '-0.5',
      trend: 'down',
      icon: TrendingUp,
      color: 'text-threat-info',
      bgColor: 'bg-threat-info/10',
      borderColor: 'border-threat-info/30'
    },
    {
      label: 'Intelligence Sources',
      value: data?.metrics?.intelligence_sources || '24',
      change: '+1',
      trend: 'up',
      icon: Eye,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/30'
    },
    {
      label: 'Graph Nodes',
      value: data?.metrics?.graph_nodes || '1.2K',
      change: '+156',
      trend: 'up',
      icon: Network,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/30'
    },
    {
      label: 'Active Collections',
      value: data?.metrics?.active_collections || '5',
      change: '0',
      trend: 'stable',
      icon: Database,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30'
    },
    {
      label: 'I&W Alerts',
      value: data?.metrics?.iw_alerts || '3',
      change: '+2',
      trend: 'up',
      icon: AlertTriangle,
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/10',
      borderColor: 'border-yellow-500/30'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric, index) => {
        const Icon = metric.icon
        return (
          <div
            key={index}
            className={`intel-card p-6 border ${metric.borderColor} ${metric.bgColor}`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className={`p-2 rounded ${metric.bgColor}`}>
                <Icon className={`w-5 h-5 ${metric.color}`} />
              </div>
              {metric.trend !== 'stable' && (
                <div className={`flex items-center gap-1 text-xs font-medium ${
                  metric.trend === 'up' ? 'text-green-500' : 'text-red-500'
                }`}>
                  <span>{metric.change}</span>
                  <TrendingUp className={`w-3 h-3 ${
                    metric.trend === 'down' ? 'rotate-180' : ''
                  }`} />
                </div>
              )}
            </div>
            <div>
              <p className={`text-3xl font-bold ${metric.color} mb-1`}>
                {metric.value}
              </p>
              <p className="text-xs text-gray-400 uppercase tracking-wide">
                {metric.label}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )
}
