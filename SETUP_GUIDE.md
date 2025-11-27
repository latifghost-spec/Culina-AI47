# 🍽️ CulinaAI Setup Guide - Google Sign-In Configuration

## Current Status ✅
- ✅ **Logo version restored**: The polished frontend with CulinaAI branding is now active
- ✅ **Backend running**: FastAPI server operational on http://localhost:8000
- ✅ **Frontend accessible**: Available at http://localhost:8000/app/index.html
- ✅ **Google sign-in implemented**: Both frontend and backend code ready
- ✅ **Registration fixed**: Proper validation and error handling

## 🔧 Google Sign-In Setup

To enable Google sign-in, you need to configure your Google OAuth credentials:

### 1. Get Google Client ID
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000`
   - Authorized JavaScript origins: `http://localhost:8000`
5. Copy your Client ID

### 2. Update Configuration
Replace `your-google-client-id-here` in these files:

**Backend (.env file):**
```
GOOGLE_CLIENT_ID=YOUR_ACTUAL_GOOGLE_CLIENT_ID
```

**Frontend (index.html line 13):**
```html
<meta name="google-signin-client_id" content="YOUR_ACTUAL_GOOGLE_CLIENT_ID">
```

### 3. Restart Backend
```bash
cd "c:\Users\Mega Pc\CulinaAI\backend"
python main.py
```

## 🎨 Features Available Now

### ✅ Authentication
- Traditional email/password registration (with proper validation)
- Google sign-in (once configured)
- Professional glassmorphism design with CulinaAI branding
- Responsive layout

### ✅ Menu Generation
- AI-powered menu creation
- Real-time pricing integration
- Seasonal and regional options
- PDF export functionality

### ✅ Professional Design
- CulinaAI logo integration
- Modern gradient backgrounds
- Glassmorphism effects
- Professional color scheme

## 🚀 Quick Test

1. **Access the app**: http://localhost:8000/app/index.html
2. **Test registration**: Try registering with a valid username (no spaces)
3. **Generate menu**: Login and create a Mediterranean menu
4. **Configure Google**: Add your Google Client ID for social login

## 📝 Notes

- The supplier management system is still available in the backend but the frontend focuses on the core menu generation experience
- All API endpoints are properly configured with `/api/` prefix
- Database is automatically created on first run
- CORS is enabled for frontend access

Enjoy your restored CulinaAI platform with professional branding! 🍽️✨