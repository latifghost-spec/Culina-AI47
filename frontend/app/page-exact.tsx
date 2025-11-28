'use client'

import Link from 'next/link'
import { ChefHat, Rocket, Settings, BarChart3, Package, Video, DollarSign, Users, FileText, MessageCircle, HelpCircle, Twitter, Instagram, Github, Linkedin } from 'lucide-react'

export default function ExactLandingPage() {

  const handleStartNow = () => {
    window.location.href = '/ideation'
  }

  const handleConfigureAPI = () => {
    alert('API Configuration panel would open here')
  }

  return (
    <div className="min-h-screen hero-gradient">
      {/* Navigation */}
      <nav className="nav-container">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <ChefHat className="w-8 h-8 text-cyan-400" />
              <span className="text-2xl font-bold text-white">CulinaAI</span>
            </div>
            
            {/* Navigation Links */}
            <div className="hidden lg:flex items-center space-x-8">
              <Link href="/dashboard" className="nav-link">Dashboard</Link>
              <Link href="/inventory" className="nav-link">Inventory</Link>
              <Link href="/ideation" className="nav-link">Menu Generator</Link>
              <Link href="/video" className="nav-link">Video Creator</Link>
              <Link href="/suppliers" className="nav-link">Suppliers</Link>
              <Link href="/financial" className="nav-link">Financial</Link>
              <Link href="/ai-prompts" className="nav-link">AI Prompts</Link>
            </div>
            
            {/* Auth Buttons */}
            <div className="flex items-center space-x-4">
              <Link href="/login" className="text-white hover:text-cyan-400 transition-colors font-medium">
                Login
              </Link>
              <button className="bg-cyan-500 hover:bg-cyan-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                Demo Mode
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-fadeInUp">
            {/* Main Headline */}
            <h1 className="hero-title text-white">
              STOP WASTING TIME
            </h1>
            
            {/* Secondary Headline with Cyan Glow */}
            <h2 className="hero-subtitle cyan-glow">
              JOIN CULINAAI
            </h2>
            
            {/* Description */}
            <p className="hero-description">
              Your AI-powered culinary intelligence platform. Chef AI technology with complete inventory management, 
              CAPEX/OPEX analysis, supplier integration, and Velo 3 AI video generation. 
              Professional-grade tools for serious chefs.
            </p>
            
            {/* CTA Buttons */}
            <div className="cta-container">
              <button 
                onClick={handleStartNow}
                className="btn-primary flex items-center space-x-2"
              >
                <Rocket className="cta-icon" />
                <span>Start Now</span>
              </button>
              
              <button 
                onClick={handleConfigureAPI}
                className="btn-secondary flex items-center space-x-2"
              >
                <Settings className="cta-icon" />
                <span>Configure API</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer-container">
        <div className="footer-grid">
          {/* CulinaAI Column */}
          <div className="footer-column">
            <div className="flex items-center space-x-3 mb-4">
              <ChefHat className="w-6 h-6 text-cyan-400" />
              <h3>CulinaAI</h3>
            </div>
            <p>Your Complete AI-Powered Culinary Intelligence Platform</p>
          </div>
          
          {/* Product Column */}
          <div className="footer-column">
            <h3>Product</h3>
            <ul>
              <li><Link href="/menu-generator" className="flex items-center space-x-2"><Package className="w-4 h-4" /> Menu Generator</Link></li>
              <li><Link href="/video-creator" className="flex items-center space-x-2"><Video className="w-4 h-4" /> Video Creator</Link></li>
              <li><Link href="/inventory" className="flex items-center space-x-2"><BarChart3 className="w-4 h-4" /> Inventory Management</Link></li>
              <li><Link href="/financial" className="flex items-center space-x-2"><DollarSign className="w-4 h-4" /> Financial Analytics</Link></li>
            </ul>
          </div>
          
          {/* Resources Column */}
          <div className="footer-column">
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
          <div className="footer-column">
            <h3>Connect</h3>
            <div className="social-icons">
              <a href="#" className="social-icon" aria-label="Twitter">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="social-icon" aria-label="Instagram">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="#" className="social-icon" aria-label="GitHub">
                <Github className="w-5 h-5" />
              </a>
              <a href="#" className="social-icon" aria-label="LinkedIn">
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
        
        {/* Bottom Footer */}
        <div className="footer-bottom">
          <p>© 2024 CulinaAI. All rights reserved. Powered by Velo 3 AI & Gemini Technology.</p>
        </div>
      </footer>
    </div>
  )
}
