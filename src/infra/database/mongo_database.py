import threading

from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from config import settings

_mongo_client: MongoClient | None = None
_client_lock = threading.Lock()


def get_client() -> MongoClient:
    global _mongo_client
    if _mongo_client is None:
        with _client_lock:
            if _mongo_client is None:
                _mongo_client = MongoClient(settings.MONGO_URI, server_api=ServerApi("1"))
    return _mongo_client


def get_database() -> Database:
    return get_client()[settings.MONGO_DATABASE_NAME]
