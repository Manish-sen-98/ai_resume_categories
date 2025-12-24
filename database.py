import motor.motor_asyncio
import os
import certifi  # <--- Essential for fixing SSL errors on Windows
from dotenv import load_dotenv

load_dotenv()

mongo_url = os.getenv("MONGO_URL")

# --- ROBUST SSL CONFIGURATION ---
client = motor.motor_asyncio.AsyncIOMotorClient(
    mongo_url,
    # 1. Force Secure Connection
    tls=True,
    # 2. CRITICAL: Bypass all certificate verification errors
    tlsAllowInvalidCertificates=True,
    # 3. Provide the 'certifi' bundle as a fallback for the handshake
    tlsCAFile=certifi.where()
)

db = client.resume_sorter_db
resumes_collection = db.resumes

async def save_resume_data(data: dict):
    result = await resumes_collection.insert_one(data)
    return result.inserted_id