import google.generativeai as genai
import json
import os
import pymupdf 

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# CHANGED: Variable name is now 'file_bytes' to be clear it's not a path
async def analyze_resume(file_bytes):
    
    # --- FIX IS HERE ---
    # We must use 'stream=' and 'filetype=' so PyMuPDF knows it's memory data
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    
    # The rest of your logic stays the same
    text = chr(12).join([page.get_text() for page in doc])
    
    model = genai.GenerativeModel('gemini-2.5-flash') # Or 'gemini-1.5-flash'
    prompt = f"""
    Act as an HR Expert. Categorize this resume into 'Web_Dev','Dev_Ops', 'Data_Science', or 'Mobile_Dev'.
    Give it a score out of 100. Return ONLY JSON like this:
    {{"name": "string", "category": "string", "score": int}}
    Resume Text: {text[:2000]}
    """
    
    response = model.generate_content(prompt)
    
    # Clean up response
    data = response.text.strip().replace('```json', '').replace('```', '')
    return json.loads(data)