# CulinaAI - Complete Testing Guide

## ✅ Status Summary
- **Frontend**: Fixed and validated (0 errors)
- **Backend**: Fixed and validated (0 errors)
- **Dependencies**: All installed and updated
- **Ready for**: Full end-to-end testing

---

## Quick Start - Running the Application

### Step 1: Start the Backend Server
```powershell
cd "C:\Users\Mega Pc\CulinaAI"
& ".\.venv\Scripts\python.exe" -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
Uvicorn running on http://0.0.0.0:8000
Press CTRL+C to quit
```

### Step 2: Open Frontend in Browser
1. Open `frontend/index.html` in your web browser
2. OR navigate to: `http://localhost:8000` (if serving from backend)

---

## Feature Testing Checklist

### 🔐 Authentication
- [ ] Login button displays correctly
- [ ] Register button displays correctly
- [ ] Google Sign-In button appears
- [ ] Login modal opens on click
- [ ] Register modal opens on click
- [ ] Google OAuth redirects properly

### 🍽️ Menu Management
- [ ] "Generate Menu" button visible
- [ ] Menu generation form displays all fields
- [ ] Cuisine selection dropdown works
- [ ] Budget range slider works
- [ ] "Generate AI Menu" button triggers API call
- [ ] Loading indicator shows during generation
- [ ] Generated menu displays correctly with items

### 📊 Financial Analysis
- [ ] "Analyze P&L" section displays
- [ ] Financial metrics update after generation
- [ ] Profit/loss calculations shown
- [ ] Cost breakdown displayed

### 🎬 Video Generation
- [ ] Video generation button appears on menu items
- [ ] "Creating Video..." indicator shows
- [ ] Status polling works (checks every 5 seconds)
- [ ] Video displays when ready
- [ ] Timeout message after 10 minutes if needed

### 📦 Supplier Management
- [ ] Supplier list displays
- [ ] Add supplier form works
- [ ] Supplier inventory updates shown
- [ ] Pricing information displayed

### 💾 Data Export
- [ ] Export to Excel button works
- [ ] PDF export functionality available
- [ ] Reports download correctly

### 🎨 UI/UX
- [ ] Color scheme matches logo (blue #00A8FF primary)
- [ ] Responsive design on mobile (< 768px)
- [ ] Responsive design on tablet (768px - 1024px)
- [ ] Responsive design on desktop (> 1024px)
- [ ] Dark mode styling visible
- [ ] Animations smooth and non-intrusive
- [ ] Glass morphism effect visible on glass elements

### 🌐 Responsive Design
- [ ] Test on mobile (320px - 480px)
- [ ] Test on tablet (768px - 1024px)
- [ ] Test on desktop (1920px+)
- [ ] Verify text readability at all sizes
- [ ] Check button tap areas on mobile (min 44px)

---

## API Endpoint Testing

### Authentication Endpoints
```bash
# Test user registration
POST /api/auth/register
Body: {"email": "test@example.com", "password": "Test123!", "full_name": "Test User"}

# Test user login
POST /api/auth/login
Body: {"email": "test@example.com", "password": "Test123!"}

# Test Google OAuth
POST /api/auth/google
Body: {"id_token": "...", "email": "...", "name": "..."}

# Get current user
GET /api/auth/me
Headers: {"Authorization": "Bearer {token}"}
```

### Menu Endpoints
```bash
# Generate menu
POST /api/menus/generate
Headers: {"Authorization": "Bearer {token}"}
Body: {"cuisine": "Italian", "budget": 50, "servings": 4}

# Get menus
GET /api/menus
Headers: {"Authorization": "Bearer {token}"}
```

### Video Endpoints
```bash
# Generate video
POST /api/videos/generate-menu-item
Headers: {"Authorization": "Bearer {token}"}
Body: {"menu_item": "Pasta Carbonara", "description": "..."}

# Check video status
GET /api/videos/status/{job_id}
Headers: {"Authorization": "Bearer {token}"}
```

---

## Common Issues & Solutions

### Issue: Server won't start
**Solution**: 
- Make sure all packages are installed: `pip install -r requirements.txt`
- Check port 8000 is not in use
- Verify Python virtual environment is activated

### Issue: Google Sign-In not working
**Solution**:
- Check Google Client ID is configured in `index.html`
- Verify Google OAuth app is set up in Google Cloud Console
- Check redirect URI matches your app URL

### Issue: Video generation fails
**Solution**:
- Ensure Google Gemini API key is configured
- Check backend has internet connection for API calls
- Verify Velo3 API credentials if using that service

### Issue: Database connection fails
**Solution**:
- Check DATABASE_URL environment variable
- Verify PostgreSQL is running (if using Render.com)
- Check connection string in `.env` file

---

## Performance Testing

- [ ] Page load time < 3 seconds
- [ ] API response time < 2 seconds
- [ ] Video generation < 60 seconds
- [ ] Memory usage stable during polling
- [ ] No memory leaks during extended use

---

## Security Testing

- [ ] JWT token validation working
- [ ] Password hashing verified
- [ ] CORS headers correct
- [ ] SQL injection attempts blocked
- [ ] XSS prevention active

---

## Final Validation Checklist

- [ ] Zero console errors
- [ ] Zero network 404 errors
- [ ] All API responses return valid JSON
- [ ] Error messages display properly
- [ ] Notifications show correctly
- [ ] Loading states work
- [ ] All buttons are clickable
- [ ] Forms validate input properly

---

## Success Criteria

✅ **All tests should pass for production deployment**

Once testing is complete:
1. Review any failed tests
2. Fix issues if found
3. Re-run failed tests
4. Document any deviations
5. Prepare for deployment

---

Generated: 2024
Ready for testing!
