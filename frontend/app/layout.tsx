import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({ 
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Sentinel Intelligence Platform',
  description: 'Intelligence-driven security operations platform applying IC methodology to cybersecurity',
  keywords: ['intelligence', 'security', 'cybersecurity', 'threat intelligence', 'OSINT', 'cyber'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
        {/* Classification Banner */}
        <div className="classification-banner">
          UNCLASSIFIED//FOR OFFICIAL USE ONLY
        </div>
        
        {/* Main Content */}
        <main className="min-h-screen">
          {children}
        </main>
        
        {/* Footer Classification Banner */}
        <div className="classification-banner">
          UNCLASSIFIED//FOR OFFICIAL USE ONLY
        </div>
      </body>
    </html>
  )
}
