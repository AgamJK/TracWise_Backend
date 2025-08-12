import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["manuals_db"]

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")