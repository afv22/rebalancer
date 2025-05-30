import os

import firebase_admin
from firebase_admin import credentials, firestore

from app.utils import is_prod


def initialize_firebase():
    # Check if Firebase Admin is already initialized
    if not firebase_admin._apps:
        if is_prod():
            # If running in production environment like Google Cloud, use default credentials
            cred = credentials.ApplicationDefault()
        else:
            # For local development, use the service account file
            cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
            cred = credentials.Certificate(cred_path)

        firebase_admin.initialize_app(cred)


class FirestoreClient:
    _items = None

    @classmethod
    def query_items(cls):
        initialize_firebase()

        if not cls._items:
            db = firestore.client()
            cls._items = db.collection("items")

        return cls._items
