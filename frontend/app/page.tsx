'use client'

import { Shield, Activity, Database, Network, Target, AlertTriangle, TrendingUp, Eye, ArrowRight } from 'lucide-react'
import { useEffect, useState } from 'react'
import Link from 'next/link'

export default function HomePage() {
  const [systemStatus, setSystemStatus] = useState('INITIALIZING')
  const [timestamp, setTimestamp] = useState('')

  useEffect(() => {
    // Simulate system initialization
    setTimeout(() => setSystemStatus('OPERATIONAL'), 1000)
    
    // Update timestamp
    const updateTime = () => {
      const now = new Date()
      setTimestamp(now.toISOString().replace('T', ' ').split('.')[0] + 'Z')
    }
    updateTime()
    const interval = setInterval(updateTime, 1000)
    return () => clearInterval(interval)
  }, [])

  const services = [
    { name: 'ASM Service', status: 'STANDBY', icon: Target, description: 'Attack Surface Management' },
    { name: 'OSINT Service', status: 'STANDBY', icon: Eye, description: 'Open Source Intelligence' },
    { name: 'SIGINT Service', status: 'STANDBY', icon: Activity, description: 'Signals Intelligence' },
    { name: 'CYBINT Service', status: 'STANDBY', icon: Shield, description: 'Cyber Intelligence' },
    { name: 'Fusion Engine', status: 'STANDBY', icon: Network, description: 'Multi-INT Fusion' },
    { name: 'Analytics Engine', status: 'STANDBY', icon: TrendingUp, description: 'Intelligence Analytics' },
  ]

  const stats = [
    { label: 'Assets Monitored', value: '0', color: 'text-cyber-primary' },
    { label: 'Threats Tracked', value: '0', color: 'text-threat-warning' },
    { label: 'Intel Reports', value: '0', color: 'text-threat-info' },
    { label: 'Active Collections', value: '0', color: 'text-classified-unclassified' },
  ]

  return (
    <div className="min-h-screen bg-intel-bg grid-background">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <header className="mb-12 fade-in">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-cyber-primary mb-2 terminal-text">
                SENTINEL
              </h1>
              <p className="text-gray-400 text-sm font-mono">
                Intelligence-Driven Security Operations Platform
              </p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 justify-end mb-1">
                <span className="font-mono text-xs text-gray-500">SYSTEM STATUS:</span>
                <span className={`font-mono text-sm font-bold ${
                  systemStatus === 'OPERATIONAL' ? 'text-classified-unclassified' : 'text-classified-cui'
                }`}>
                  {systemStatus}
                </span>
                {systemStatus === 'OPERATIONAL' && (
                  <span className="w-2 h-2 bg-classified-unclassified rounded-full status-pulse"></span>
                )}
              </div>
              <div className="font-mono text-xs text-gray-500">
                {timestamp}
              </div>
            </div>
          </div>
          
          <div className="h-px bg-gradient-to-r from-transparent via-cyber-primary to-transparent"></div>
        </header>

        {/* System Overview */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-white mb-6 font-mono flex items-center gap-2">
            <Database className="w-5 h-5 text-cyber-primary" />
            SYSTEM OVERVIEW
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {stats.map((stat, idx) => (
              <div key={idx} className="intel-card p-6">
                <div className="text-gray-400 text-xs font-mono uppercase mb-2">
                  {stat.label}
                </div>
                <div className={`text-3xl font-bold ${stat.color} font-mono`}>
                  {stat.value}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Intelligence Services Status */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-white mb-6 font-mono flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyber-primary" />
            INTELLIGENCE SERVICES
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {services.map((service, idx) => {
              const Icon = service.icon
              return (
                <div key={idx} className="intel-card p-6 group">
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 bg-intel-bg rounded-lg group-hover:bg-cyber-primary/10 transition-colors">
                      <Icon className="w-6 h-6 text-cyber-primary" />
                    </div>
                    <span className={`text-xs font-mono px-2 py-1 rounded ${
                      service.status === 'OPERATIONAL' 
                        ? 'bg-classified-unclassified/20 text-classified-unclassified' 
                        : 'bg-classified-cui/20 text-classified-cui'
                    }`}>
                      {service.status}
                    </span>
                  </div>
                  <h3 className="text-white font-semibold mb-2">{service.name}</h3>
                  <p className="text-gray-400 text-sm">{service.description}</p>
                </div>
              )
            })}
          </div>
        </section>

        {/* Intelligence Capabilities */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-white mb-6 font-mono flex items-center gap-2">
            <Shield className="w-5 h-5 text-cyber-primary" />
            INTELLIGENCE CAPABILITIES
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* OSINT */}
            <div className="intel-card p-6 border-l-4 border-l-cyber-primary">
              <h3 className="text-cyber-primary font-bold text-lg mb-3 font-mono">OSINT</h3>
              <p className="text-gray-300 text-sm mb-4">Open Source Intelligence Collection</p>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-cyber-primary rounded-full"></span>
                  Dark web monitoring and paste sites
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-cyber-primary rounded-full"></span>
                  Certificate transparency logs
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-cyber-primary rounded-full"></span>
                  GitHub security advisories
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-cyber-primary rounded-full"></span>
                  Threat intelligence feeds
                </li>
              </ul>
            </div>

            {/* SIGINT */}
            <div className="intel-card p-6 border-l-4 border-l-cyber-secondary">
              <h3 className="text-cyber-secondary font-bold text-lg mb-3 font-mono">SIGINT</h3>
              <p className="text-gray-300 text-sm mb-4">Signals Intelligence Analysis</p>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-cyber-secondary rounded-full"></span>
                  Network traffic anomaly detection
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-cyber-secondary rounded-full"></span>
                  C2 beaconing identification
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-cyber-secondary rounded-full"></span>
                  Protocol analysis and fingerprinting
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-cyber-secondary rounded-full"></span>
                  Data exfiltration detection
                </li>
              </ul>
            </div>

            {/* CYBINT */}
            <div className="intel-card p-6 border-l-4 border-l-cyber-accent">
              <h3 className="text-cyber-accent font-bold text-lg mb-3 font-mono">CYBINT</h3>
              <p className="text-gray-300 text-sm mb-4">Cyber Intelligence & Vulnerability Mgmt</p>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-cyber-accent rounded-full"></span>
                  Vulnerability scanning and CVE tracking
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-cyber-accent rounded-full"></span>
                  Exploit availability assessment
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-cyber-accent rounded-full"></span>
                  Patch status monitoring
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-cyber-accent rounded-full"></span>
                  Weaponization likelihood scoring
                </li>
              </ul>
            </div>

            {/* Fusion */}
            <div className="intel-card p-6 border-l-4 border-l-threat-warning">
              <h3 className="text-threat-warning font-bold text-lg mb-3 font-mono">ALL-SOURCE FUSION</h3>
              <p className="text-gray-300 text-sm mb-4">Multi-INT Intelligence Correlation</p>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-threat-warning rounded-full"></span>
                  Cross-source indicator correlation
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-threat-warning rounded-full"></span>
                  Knowledge graph relationship mapping
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-threat-warning rounded-full"></span>
                  Confidence scoring and gap analysis
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-threat-warning rounded-full"></span>
                  Threat campaign reconstruction
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Quick Access */}
        <section>
          <h2 className="text-xl font-bold text-white mb-6 font-mono flex items-center gap-2">
            <Target className="w-5 h-5 text-cyber-primary" />
            QUICK ACCESS
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a href="/api/docs" target="_blank" className="intel-card p-6 block group cursor-pointer">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-white font-semibold">API Documentation</h3>
                <ArrowRight className="w-5 h-5 text-cyber-primary opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <p className="text-gray-400 text-sm">Interactive API documentation and testing</p>
            </a>
            
            <Link href="/dashboard" className="intel-card p-6 block group cursor-pointer">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-white font-semibold">Intelligence Dashboard</h3>
                <ArrowRight className="w-5 h-5 text-cyber-primary opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <p className="text-gray-400 text-sm">Real-time intelligence operations center</p>
            </Link>
            
            <div className="intel-card p-6 opacity-50">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-white font-semibold">Asset Discovery</h3>
                <span className="text-xs bg-classified-cui/20 text-classified-cui px-2 py-1 rounded font-mono">COMING SOON</span>
              </div>
              <p className="text-gray-400 text-sm">Initiate attack surface discovery</p>
            </div>
          </div>
        </section>

        {/* System Notice */}
        <div className="mt-12 intel-card p-6 border-l-4 border-l-green-500">
          <div className="flex items-start gap-4">
            <Shield className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-white font-semibold mb-2 font-mono">SYSTEM STATUS</h3>
              <p className="text-gray-400 text-sm">
                Sentinel is now in <span className="text-cyber-primary font-semibold">Phase 6: UI & Visualization</span>. 
                Intelligence collection, fusion, analytics, and product generation services are <span className="text-green-500 font-semibold">OPERATIONAL</span>. 
                Intelligence dashboard with interactive visualizations now available. 
                Progress: <span className="text-cyber-primary font-semibold">6 of 7 phases complete (86%)</span>.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
