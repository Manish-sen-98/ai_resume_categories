from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import pandas as pd
from typing import List
import cloudinary
import cloudinary.uploader
from database import save_resume_data, resumes_collection
from ai_service import analyze_resume
from fastapi.concurrency import run_in_threadpool
import os

app = FastAPI(title="AI Resume Sorter")

# --- 1. CLOUDINARY CONFIGURATION ---
cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "your_cloud_name"), 
  api_key = os.getenv("CLOUDINARY_API_KEY", "your_api_key"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET", "your_api_secret"),
  secure = True
)

@app.post("/upload")
async def upload_resumes(files: List[UploadFile] = File(...)):
    results = []
    
    for file in files:
        # --- STEP 1: READ INTO MEMORY ---
        file_content = await file.read()
        
        # --- STEP 2: AI ANALYSIS (IN-MEMORY) ---
       
        analysis = await analyze_resume(file_content)
        
        # --- STEP 3: CLOUDINARY UPLOAD (IN-MEMORY) ---
        
        upload_result = cloudinary.uploader.upload(
            file_content, 
            folder=f"resumes/{analysis.get('category', 'Uncategorized')}", 
            resource_type="auto"
        )
        
        # Get the public URL
        cloud_url = upload_result.get("secure_url")
        
        # --- STEP 4: SAVE TO DB ---
        # Update the analysis object with the Cloud URL instead of a local path
        analysis["file_path"] = cloud_url
        
        inserted_id = await save_resume_data(analysis)
        analysis["_id"] = str(inserted_id) 

        results.append(analysis)
    
    return {"status": "success", "processed": len(files), "data": results}

@app.get("/export-data")
async def export_excel():
    cursor = resumes_collection.find({}, {"_id": 0, "name": 1, "score": 1, "category": 1})
    data = await cursor.to_list(length=1000) 

    return data