import Link from 'next/link'

export default function ModernLandingPage() {
  return (
    <div className="hero-gradient-modern">
      {/* Navigation */}
      <nav className="nav-modern">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center">
                <span className="text-black font-bold text-xl">C</span>
              </div>
              <span className="text-2xl font-bold neon-glow">CulinaAI</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <Link href="#" className="nav-link-modern">Dashboard</Link>
              <Link href="#" className="nav-link-modern">Inventory</Link>
              <Link href="#" className="nav-link-modern">Menu Generator</Link>
              <Link href="#" className="nav-link-modern">Analytics</Link>
              <Link href="#" className="nav-link-modern">Settings</Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/ideation" className="btn-modern-primary">
                Launch App
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="hero-modern">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <div className="animate-float-modern">
            <h1 className="hero-title-modern">
              STOP WASTING
            </h1>
            <h2 className="hero-subtitle-modern neon-glow">
              TIME
            </h2>
          </div>
          
          <p className="hero-description-modern">
            Transform your culinary business with AI-powered menu optimization, 
            inventory management, and cost analysis. Join thousands of chefs and 
            restaurant owners who are revolutionizing their kitchens.
          </p>

          <div className="cta-modern-container">
            <Link href="/ideation" className="btn-modern-primary animate-glow-pulse">
              <span>🚀</span>
              Start Now
            </Link>
            <Link href="#" className="btn-modern-secondary">
              <span>⚙️</span>
              Configure API
            </Link>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20">
            <div className="glass-container p-6 text-center">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-bold mb-2 neon-glow">AI-Powered</h3>
              <p className="text-gray-300">Smart menu generation and optimization using advanced AI algorithms</p>
            </div>
            <div className="glass-container p-6 text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-bold mb-2 neon-glow">Real-time Analytics</h3>
              <p className="text-gray-300">Live cost analysis and nutritional insights for every dish</p>
            </div>
            <div className="glass-container p-6 text-center">
              <div className="text-4xl mb-4">💰</div>
              <h3 className="text-xl font-bold mb-2 neon-glow">Cost Optimization</h3>
              <p className="text-gray-300">Reduce waste and maximize profit with intelligent inventory management</p>
            </div>
          </div>
        </div>
      </div>

      {/* Modern Footer */}
      <footer className="footer-modern">
        <div className="footer-modern-grid">
          <div className="footer-modern-column">
            <h3>CulinaAI</h3>
            <p>
              Revolutionizing the culinary industry with AI-powered solutions 
              that help chefs and restaurant owners optimize their operations.
            </p>
            <div className="social-modern-icons">
              <Link href="#" className="social-modern-icon">f</Link>
              <Link href="#" className="social-modern-icon">t</Link>
              <Link href="#" className="social-modern-icon">in</Link>
              <Link href="#" className="social-modern-icon">ig</Link>
            </div>
          </div>
          <div className="footer-modern-column">
            <h3>Product</h3>
            <ul>
              <li><Link href="#">Menu Generator</Link></li>
              <li><Link href="#">Inventory Management</Link></li>
              <li><Link href="#">Cost Analytics</Link></li>
              <li><Link href="#">Nutrition Analysis</Link></li>
              <li><Link href="#">Recipe Optimization</Link></li>
            </ul>
          </div>
          <div className="footer-modern-column">
            <h3>Resources</h3>
            <ul>
              <li><Link href="#">Documentation</Link></li>
              <li><Link href="#">API Reference</Link></li>
              <li><Link href="#">Video Tutorials</Link></li>
              <li><Link href="#">Blog</Link></li>
              <li><Link href="#">Community</Link></li>
            </ul>
          </div>
          <div className="footer-modern-column">
            <h3>Connect</h3>
            <ul>
              <li><Link href="#">Contact Support</Link></li>
              <li><Link href="#">Schedule Demo</Link></li>
              <li><Link href="#">Partner Program</Link></li>
              <li><Link href="#">Careers</Link></li>
              <li><Link href="#">Press Kit</Link></li>
            </ul>
          </div>
        </div>
        <div className="footer-modern-bottom">
          <p>&copy; 2024 CulinaAI. All rights reserved. | Privacy Policy | Terms of Service</p>
        </div>
      </footer>
    </div>
  )
}