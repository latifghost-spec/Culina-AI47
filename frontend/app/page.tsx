'use client'

import Link from 'next/link'
import { ChefHat, Rocket, Settings, BarChart3, Package, Video, DollarSign, Users, FileText, MessageCircle, HelpCircle, Twitter, Instagram, Github, Linkedin } from 'lucide-react'

export default function ModernEnhancedLandingPage() {

  const handleConfigureAPI = () => {
    alert('API Configuration panel would open here')
  }

  return (
    <div className="hero-gradient-modern">
      {/* Navigation */}
      <nav className="nav-modern">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <ChefHat className="w-8 h-8 text-cyan-400" />
              <span className="text-2xl font-bold neon-glow">CulinaAI</span>
            </div>
            
            {/* Navigation Links */}
            <div className="hidden lg:flex items-center space-x-8">
              <Link href="/" prefetch={false} className="nav-link-modern">Dashboard</Link>
              <Link href="/inventory" prefetch={false} className="nav-link-modern">Inventory</Link>
              <Link href="/ideation" prefetch={false} className="nav-link-modern">Menu Generator</Link>
              <Link href="/video" prefetch={false} className="nav-link-modern">Video Creator</Link>
              <Link href="/suppliers" prefetch={false} className="nav-link-modern">Suppliers</Link>
              <Link href="/financial" prefetch={false} className="nav-link-modern">Financial</Link>
              <Link href="/ai-prompts" prefetch={false} className="nav-link-modern">AI Prompts</Link>
            </div>
            
            {/* Demo Version */}
            <div className="flex items-center space-x-4">
              <div className="px-3 py-1 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full text-xs font-semibold text-white">
                DEMO v2.0
              </div>
              <Link href="/ideation" className="bg-cyan-500 hover:bg-cyan-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-modern">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-fadeInUp">
            {/* Main Headline */}
            <h1 className="hero-title-modern">
              STOP WASTING
            </h1>
            
            {/* Secondary Headline with Cyan Glow */}
            <h2 className="hero-subtitle-modern neon-glow">
              TIME
            </h2>
            
            {/* Description */}
            <p className="hero-description-modern">
              Your AI-powered culinary intelligence platform. Chef AI technology with complete inventory management, 
              CAPEX/OPEX analysis, supplier integration, and Velo 3 AI video generation. 
              Professional-grade tools for serious chefs.
            </p>
            
            {/* CTA Buttons */}
            <div className="cta-modern-container">
              <Link 
                href="/ideation"
                className="btn-modern-primary animate-glow-pulse flex items-center space-x-2"
              >
                <Rocket className="text-xl" />
                <span>Start Now</span>
              </Link>
              
              <button 
                onClick={handleConfigureAPI}
                className="btn-modern-secondary flex items-center space-x-2"
              >
                <Settings className="text-xl" />
                <span>Configure API</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer-modern">
        <div className="footer-modern-grid">
          {/* CulinaAI Column */}
          <div className="footer-modern-column">
            <div className="flex items-center space-x-3 mb-4">
              <ChefHat className="w-6 h-6 text-cyan-400" />
              <h3>CulinaAI</h3>
            </div>
            <p>Your Complete AI-Powered Culinary Intelligence Platform</p>
          </div>
          
          {/* Product Column */}
          <div className="footer-modern-column">
            <h3>Product</h3>
            <ul>
              <li><Link href="/menu-generator" className="flex items-center space-x-2"><Package className="w-4 h-4" /> Menu Generator</Link></li>
              <li><Link href="/video-creator" className="flex items-center space-x-2"><Video className="w-4 h-4" /> Video Creator</Link></li>
              <li><Link href="/inventory" className="flex items-center space-x-2"><BarChart3 className="w-4 h-4" /> Inventory Management</Link></li>
              <li><Link href="/financial" className="flex items-center space-x-2"><DollarSign className="w-4 h-4" /> Financial Analytics</Link></li>
            </ul>
          </div>
          
          {/* Resources Column */}
          <div className="footer-modern-column">
            <h3>Resources</h3>
            <ul>
              <li><Link href="/documentation" className="flex items-center space-x-2"><FileText className="w-4 h-4" /> Documentation</Link></li>
              <li><Link href="/api-docs" className="flex items-center space-x-2"><FileText className="w-4 h-4" /> API Documentation</Link></li>
              <li><Link href="/api-reference" className="flex items-center space-x-2"><FileText className="w-4 h-4" /> API Reference</Link></li>
              <li><Link href="/community" className="flex items-center space-x-2"><Users className="w-4 h-4" /> Chef Community</Link></li>
              <li><Link href="/support" className="flex items-center space-x-2"><MessageCircle className="w-4 h-4" /> Support & AI</Link></li>
              <li><Link href="/credits" className="flex items-center space-x-2"><HelpCircle className="w-4 h-4" /> Credits</Link></li>
            </ul>
          </div>
          
          {/* Connect Column */}
          <div className="footer-modern-column">
            <h3>Connect</h3>
            <div className="social-modern-icons">
              <a href="#" className="social-modern-icon" aria-label="Twitter">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="social-modern-icon" aria-label="Instagram">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="#" className="social-modern-icon" aria-label="GitHub">
                <Github className="w-5 h-5" />
              </a>
              <a href="#" className="social-modern-icon" aria-label="LinkedIn">
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
        
        {/* Bottom Footer */}
        <div className="footer-modern-bottom">
          <p>© 2024 CulinaAI. All rights reserved. Powered by Velo 3 AI & Gemini Technology.</p>
        </div>
      </footer>
    </div>
  )
}
