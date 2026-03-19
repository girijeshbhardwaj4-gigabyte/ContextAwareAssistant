from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from config import Config

# Initialize Flask App
app = Flask(__name__)
# Load configuration from our config.py file
app.config.from_object(Config)

# Enable CORS (Allows Web/Android to communicate with this API safely without cross-origin blocks)
CORS(app)

# Initialize Database Connection
try:
    # Connect to MongoDB using the URI from our config
    client = MongoClient(app.config['MONGO_URI'])
    app.db = client.get_database() # Gets the default 'smart_assistant' database from the URI and attaches it to the app
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Register Blueprints
from routes.auth_routes import auth_bp
from routes.session_routes import session_bp
from routes.context_routes import context_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(session_bp, url_prefix='/api/sessions')
app.register_blueprint(context_bp, url_prefix='/api/context')

# Basic Route: Health Check to test if the server is running
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "success",
        "message": "Welcome to the Context-Aware Smart Assistant API!"
    }), 200

if __name__ == '__main__':
    # Run the server in debug mode for development (auto-restarts on code changes)
    app.run(host='0.0.0.0', port=5000, debug=True)
