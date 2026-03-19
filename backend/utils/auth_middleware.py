from functools import wraps
from flask import request, jsonify, current_app
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if the token is passed in the Authorization header
        if 'Authorization' in request.headers:
            # The format is usually "Bearer <token>"
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
            else:
                token = auth_header
                
        if not token:
            return jsonify({"error": "Token is missing! Please log in first."}), 401
            
        try:
            # Decode the token using our secret key
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            # Extract the user ID (this was stored in the token during login)
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired! Please log in again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token! Please log in again."}), 401
            
        # Call the actual route function and pass the user_id to it
        return f(current_user_id, *args, **kwargs)
        
    return decorated
