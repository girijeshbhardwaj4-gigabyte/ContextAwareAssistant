from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

# Create the blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 1. Validation
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({"error": "Missing required fields (username, email, password)"}), 400
    
    # Access the database from the current app instance (setup in app.py)
    users_collection = current_app.db['users']
    
    # 2. Check if user already exists
    if users_collection.find_one({"email": data['email']}):
        return jsonify({"error": "User with this email already exists"}), 400
        
    # 3. Hash the password for security
    hashed_password = generate_password_hash(data['password'])
    
    # 4. Create user document to insert into MongoDB
    new_user = {
        "username": data['username'],
        "email": data['email'],
        "password": hashed_password,
        "created_at": datetime.datetime.utcnow()
    }
    
    users_collection.insert_one(new_user)
    
    return jsonify({"message": "User registered successfully!"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # 1. Validation
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing email or password"}), 400
        
    users_collection = current_app.db['users']
    
    # 2. Find user in the database
    user = users_collection.find_one({"email": data['email']})
    
    # 3. Verify user exists and password matches the hash
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({"error": "Invalid email or password"}), 401
        
    # 4. Generate JWT Token (Expires in 24 hours)
    token = jwt.encode({
        'user_id': str(user['_id']),
        'email': user['email'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        "message": "Login successful",
        "token": token,
        "username": user['username']
    }), 200
