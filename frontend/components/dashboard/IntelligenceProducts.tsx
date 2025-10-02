'use client'

import { useState, useEffect } from 'react'
import { FileText, AlertTriangle, Target, TrendingUp, Download, Eye, Clock } from 'lucide-react'

interface Product {
  id: string
  type: string
  title: string
  classification: string
  generated_at: string
  summary: string
  status: string
}

export default function IntelligenceProducts() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedProduct, setSelectedProduct] = useState<any>(null)
  const [generating, setGenerating] = useState<string | null>(null)
  const [generateError, setGenerateError] = useState<string | null>(null)

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/products/recent')
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`)
      }
      const data = await response.json()
      setProducts(data.products || [])
      setError(null)
      setLoading(false)
    } catch (err) {
      console.error('Failed to fetch products:', err)
      setError('Unable to connect to backend API. Please ensure the backend service is running at http://localhost:8000')
      setLoading(false)
    }
  }

  const generateProduct = async (type: string) => {
    setGenerating(type)
    setGenerateError(null)
    
    try {
      let url = ''
      let options: RequestInit = { method: 'GET' }
      
      switch (type) {
        case 'current_intelligence':
          url = 'http://localhost:8000/api/v1/products/current-intelligence'
          break
        case 'indications_warning':
          url = 'http://localhost:8000/api/v1/products/indications-warning'
          break
        case 'executive_briefing':
          url = 'http://localhost:8000/api/v1/products/executive-briefing'
          options = { method: 'POST' }
          break
        case 'target_package':
          url = 'http://localhost:8000/api/v1/products/target-package/asset-1'
          options = { method: 'POST' }
          break
      }
      
      const response = await fetch(url, options)
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`)
      }
      const data = await response.json()
      setSelectedProduct(data)
    } catch (err) {
      console.error('Failed to generate product:', err)
      setGenerateError('Failed to generate product. Ensure backend API is running and intelligence data is available.')
    } finally {
      setGenerating(null)
    }
  }

  const productTypes = [
    {
      id: 'current_intelligence',
      name: 'Current Intelligence',
      icon: FileText,
      description: 'Daily threat briefing with key judgments',
      color: 'text-cyber-primary',
      bgColor: 'bg-cyber-primary/10',
      borderColor: 'border-cyber-primary/30'
    },
    {
      id: 'indications_warning',
      name: 'I&W Alerts',
      icon: AlertTriangle,
      description: 'Tactical warnings for imminent threats',
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/30'
    },
    {
      id: 'target_package',
      name: 'Target Package',
      icon: Target,
      description: 'Comprehensive asset intelligence',
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/10',
      borderColor: 'border-yellow-500/30'
    },
    {
      id: 'executive_briefing',
      name: 'Executive Briefing',
      icon: TrendingUp,
      description: 'Strategic assessment for leadership',
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/30'
    }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyber-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400 font-mono text-sm">Loading intelligence products...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center max-w-md">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-200 mb-2">Backend API Unavailable</h3>
          <p className="text-sm text-gray-400 mb-4">{error}</p>
          <div className="text-xs text-gray-500 bg-gray-900 border border-gray-800 rounded p-3 text-left">
            <p className="mb-2">Intelligence products require:</p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Backend API running</li>
              <li>Complete intelligence collection (ASM, OSINT, CybInt)</li>
              <li>Knowledge graph populated</li>
              <li>Product generation services operational</li>
            </ol>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {generateError && (
        <div className="bg-red-500/10 border border-red-500/30 rounded p-4 mb-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-red-400 mb-1">Generation Failed</h4>
              <p className="text-xs text-gray-400">{generateError}</p>
            </div>
          </div>
        </div>
      )}

      {/* Generate Products */}
      <div className="intel-card p-6">
        <h3 className="text-lg font-semibold text-gray-200 mb-4">Generate Intelligence Products</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {productTypes.map((type) => {
            const Icon = type.icon
            const isGenerating = generating === type.id
            
            return (
              <button
                key={type.id}
                onClick={() => generateProduct(type.id)}
                disabled={isGenerating}
                className={`
                  p-4 border rounded text-left transition-all
                  ${type.borderColor} ${type.bgColor}
                  hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed
                `}
              >
                <div className={`p-2 rounded ${type.bgColor} inline-block mb-3`}>
                  <Icon className={`w-6 h-6 ${type.color}`} />
                </div>
                <h4 className={`font-semibold ${type.color} mb-1`}>
                  {type.name}
                </h4>
                <p className="text-xs text-gray-400">
                  {isGenerating ? 'Generating...' : type.description}
                </p>
              </button>
            )
          })}
        </div>
      </div>

      {/* Recent Products */}
      <div className="intel-card p-6">
        <h3 className="text-lg font-semibold text-gray-200 mb-4">Recent Intelligence Products</h3>
        <div className="space-y-3">
          {products.map((product) => {
            const productType = productTypes.find(t => t.id === product.type)
            const Icon = productType?.icon || FileText
            
            return (
              <div
                key={product.id}
                className="flex items-start gap-4 p-4 bg-gray-900/50 border border-gray-800 rounded hover:bg-gray-800/50 transition-colors cursor-pointer"
                onClick={() => generateProduct(product.type)}
              >
                <div className={`p-2 rounded ${productType?.bgColor || 'bg-gray-800'}`}>
                  <Icon className={`w-5 h-5 ${productType?.color || 'text-gray-400'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-sm font-semibold text-gray-200">{product.title}</h4>
                    <span className="text-xs text-gray-500 font-mono">
                      {product.classification}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 mb-2">{product.summary}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(product.generated_at).toLocaleString()}
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="flex items-center gap-1 hover:text-cyber-primary">
                        <Eye className="w-3 h-3" />
                        View
                      </button>
                      <button className="flex items-center gap-1 hover:text-cyber-primary">
                        <Download className="w-3 h-3" />
                        Export
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Product Viewer */}
      {selectedProduct && (
        <div className="intel-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-200">
              {selectedProduct.product_type?.replace('_', ' ').toUpperCase()}
            </h3>
            <button
              onClick={() => setSelectedProduct(null)}
              className="px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded text-sm text-gray-300"
            >
              Close
            </button>
          </div>
          
          <div className="bg-gray-900 border border-gray-800 rounded p-6 max-h-96 overflow-y-auto">
            <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap">
              {JSON.stringify(selectedProduct, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
