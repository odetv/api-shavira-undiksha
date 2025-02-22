from src.database.firebase import db
from firebase_admin import firestore


def log_activity(log):
    log_ref = db.collection("logs").document()
    log_data = {
        "id": log_ref.id,
        "timestamp": firestore.SERVER_TIMESTAMP,
        "method": log["method"],
        "status_code": log["status_code"],
        "success": log["success"],
        "description": log["description"]
    }
    log_ref.set(log_data)