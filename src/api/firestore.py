import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from src.api.secret import GoogleSecretWrapper


class FirestoreClient:
    _items = None

    @classmethod
    def query_items(cls):
        if not firebase_admin._apps:
            maybe_cred_dict = GoogleSecretWrapper.get_secret("FirebaseCert")
            if not maybe_cred_dict:
                raise ValueError("Secret not found!")

            cred = credentials.Certificate(json.loads(maybe_cred_dict))
            firebase_admin.initialize_app(cred)

        if not cls._items:
            db = firestore.client()
            cls._items = db.collection("items")

        return cls._items
