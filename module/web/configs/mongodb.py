# mongodb.py

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
database_name = os.getenv("DATABASE_NAME")

if not all([mongo_uri, database_name]):
    raise RuntimeError("Missing required environment variables: MONGO_URI or DATABASE_NAME")

# Global MongoDB variables
client = None
db = None
collection = None
command_collection = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db, collection, command_collection
    client = AsyncIOMotorClient(mongo_uri)
    db = client[database_name]
    collection = db["data"]
    command_collection = db["command"]
    print("✅ MongoDB connected successfully.")
    yield
    client.close()
    print("❌ MongoDB connection closed.")
def get_db():
    if db is None:
        raise RuntimeError("❌ MongoDB database is not initialized.")
    return db

