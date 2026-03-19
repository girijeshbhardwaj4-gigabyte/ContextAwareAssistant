from flask import Blueprint, jsonify, current_app
from utils.auth_middleware import token_required
from services.context_engine import ContextEngine
import datetime

context_bp = Blueprint('context', __name__)

@context_bp.route('/status', methods=['GET'])
@token_required
def get_context_status(current_user_id):
    sessions_collection = current_app.db['sessions']
    
    # 1. Fetch active session
    active_session = sessions_collection.find_one({
        "user_id": current_user_id,
        "status": "active"
    })
    
    # 2. Pass data to our Context Engine (Rule-based AI)
    analysis = ContextEngine.analyze_session(active_session)
    
    # NEW: Phase 8 - Implement System Auto-Stop Database Mutation
    if analysis.get("alert") == "auto_stop" and active_session:
        end_time = datetime.datetime.utcnow()
        duration_minutes = (end_time - active_session['start_time']).total_seconds() / 60.0
        
        # Force finish the active session to prevent corrupted time leakage
        sessions_collection.update_one(
            {"_id": active_session['_id']},
            {"$set": {
                "end_time": end_time,
                "status": "completed",
                "duration_minutes": round(duration_minutes, 2),
                "auto_stopped": True
            }}
        )
        analysis["suggestion"] = f"Session automatically saved and closed after {int(duration_minutes)} minutes."
    
    return jsonify(analysis), 200
