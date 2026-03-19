from flask import Blueprint, request, jsonify, current_app
import datetime
from utils.auth_middleware import token_required

session_bp = Blueprint('sessions', __name__)

@session_bp.route('/start', methods=['POST'])
@token_required
def start_session(current_user_id):
    sessions_collection = current_app.db['sessions']
    active_session = sessions_collection.find_one({"user_id": current_user_id, "status": "active"})
    
    if active_session:
        return jsonify({"error": "You already have an active study session"}), 400
        
    data = request.get_json(silent=True) or {}
    goal = data.get('goal', "General Study")
    
    new_session = {
        "user_id": current_user_id,
        "start_time": datetime.datetime.utcnow(),
        "status": "active",
        "goal": goal,
        "last_ping": datetime.datetime.utcnow() # Track for inactivity checking
    }
    
    result = sessions_collection.insert_one(new_session)
    return jsonify({"message": "Study session started!", "session_id": str(result.inserted_id)}), 201

@session_bp.route('/ping', methods=['POST'])
@token_required
def ping_session(current_user_id):
    """Phase 8 Reminder System: User confirms they are still studying."""
    sessions_collection = current_app.db['sessions']
    active_session = sessions_collection.find_one({"user_id": current_user_id, "status": "active"})
    
    if not active_session:
        return jsonify({"error": "No active session found"}), 404
        
    # Reset inactivity timer by updating last_ping
    sessions_collection.update_one(
        {"_id": active_session['_id']},
        {"$set": {"last_ping": datetime.datetime.utcnow()}}
    )
    return jsonify({"message": "Session activity confirmed!"}), 200

@session_bp.route('/stop', methods=['POST'])
@token_required
def stop_session(current_user_id):
    sessions_collection = current_app.db['sessions']
    active_session = sessions_collection.find_one({"user_id": current_user_id, "status": "active"})
    
    if not active_session:
        return jsonify({"error": "No active study session found"}), 404
        
    end_time = datetime.datetime.utcnow()
    duration_minutes = (end_time - active_session['start_time']).total_seconds() / 60.0
    
    sessions_collection.update_one(
        {"_id": active_session['_id']},
        {"$set": {
            "end_time": end_time,
            "status": "completed",
            "duration_minutes": round(duration_minutes, 2)
        }}
    )
    return jsonify({"message": "Study session completed!", "duration_minutes": round(duration_minutes, 2)}), 200
