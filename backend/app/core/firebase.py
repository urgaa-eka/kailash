"""
Firebase Admin SDK initialization for Kailash.

Provides server-side Firebase services (auth verification, Firestore, Storage, etc.).
Configure via environment variables or a service account JSON file.

Usage:
    from app.core.firebase import firebase_app, get_firebase_app
"""

import os
import json
import logging

import firebase_admin
from firebase_admin import credentials

logger = logging.getLogger("kailash.firebase")

firebase_app = None


def _resolve_credentials():
    """Resolve Firebase credentials from env vars or file.

    Priority:
      1. FIREBASE_SERVICE_ACCOUNT_JSON — inline JSON string (CI/CD friendly)
      2. FIREBASE_SERVICE_ACCOUNT_PATH — path to .json key file
      3. GOOGLE_APPLICATION_CREDENTIALS — GCP default
      4. Application Default Credentials (GCE / Cloud Run / etc.)
    """
    # 1. Inline JSON (e.g. from GitHub secret)
    sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        try:
            info = json.loads(sa_json)
            logger.info("Firebase: using inline service-account JSON")
            return credentials.Certificate(info)
        except Exception as exc:
            logger.warning(f"Firebase: invalid inline JSON — {exc}")

    # 2. File path
    sa_path = os.environ.get(
        "FIREBASE_SERVICE_ACCOUNT_PATH",
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
    )
    if sa_path and os.path.isfile(sa_path):
        logger.info(f"Firebase: using service-account file {sa_path}")
        return credentials.Certificate(sa_path)

    # 3. Application Default Credentials
    logger.info("Firebase: using Application Default Credentials")
    return credentials.ApplicationDefault()


def init_firebase():
    """Initialise the Firebase Admin app (idempotent)."""
    global firebase_app

    if firebase_app is not None:
        return firebase_app

    # Skip if explicitly disabled
    if os.environ.get("FIREBASE_DISABLED", "").lower() in ("1", "true", "yes"):
        logger.info("Firebase: disabled via FIREBASE_DISABLED env var")
        return None

    try:
        cred = _resolve_credentials()
        firebase_app = firebase_admin.initialize_app(cred, {
            "projectId": os.environ.get("FIREBASE_PROJECT_ID", "kailash-38268"),
            "storageBucket": os.environ.get(
                "FIREBASE_STORAGE_BUCKET", "kailash-38268.firebasestorage.app"
            ),
        })
        logger.info("✅ Firebase Admin SDK initialised (project: %s)", firebase_app.project_id)
    except Exception as exc:
        logger.warning(f"⚠️ Firebase Admin SDK init failed: {exc} — continuing without Firebase")
        firebase_app = None

    return firebase_app


def get_firebase_app():
    """Return the Firebase app, initialising lazily if needed."""
    if firebase_app is None:
        return init_firebase()
    return firebase_app
