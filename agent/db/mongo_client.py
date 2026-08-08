"""Cliente MongoDB Atlas compartilhado por watcher e agente."""

import os

from pymongo import MongoClient


def get_client() -> MongoClient:
    uri = os.environ["MONGODB_URI"]
    return MongoClient(uri)
