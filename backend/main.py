from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from db import get_db, Base, get_engine 
from routes import menus, auth, suppliers, videos

# --- CRITICAL: Set up the App ---
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
app = FastAPI(title="CulinaAI Backend")

# Vercel serverless handler
handler = app

# Create Database Tables on Startup
Base.metadata.create_all(bind=get_engine())

# Enable CORS (Allows frontend access)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(menus.router, prefix="/api/menus", tags=["Menus"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["Suppliers & Inventory"])
app.include_router(videos.router, prefix="/api/videos", tags=["Video Generation"])

# Serve static files for frontend
frontend_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.isdir(frontend_dir):
    app.mount("/app", StaticFiles(directory=frontend_dir), name="app")
else:
    app.mount("/test", StaticFiles(directory="."), name="test")

@app.get("/")
def read_root():
    return {"message": "CulinaAI API is running 🚀"}