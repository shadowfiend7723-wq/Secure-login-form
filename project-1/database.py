from motor.motor_asyncio import AsyncIOMotorClient

mongo_url = "mongodb://localhost:27017/"
client = AsyncIOMotorClient(mongo_url)
# Use a lowercase name to avoid "db already exists with different case" errors on case-insensitive filesystems
db = client["new_db"]

