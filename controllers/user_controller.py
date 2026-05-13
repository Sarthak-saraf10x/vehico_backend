from flask import Blueprint, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests
import os



GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

from services.user_service import UserService


import os
from middleware.auth import require_jwt

user_bp = Blueprint('user', __name__)

class UserController:
    def __init__(self, db_config):
        self.user_service = UserService(db_config)
        
        self.jwt_secret = os.getenv("JWT_SECRET_KEY")

    def create_user(self):
        try:
            data = request.get_json()
            user = self.user_service.create_user(
                data.get('username'),
                data.get('password'),
                data.get('email'),
                data.get('full_name'),
                data.get('role')
            )
            return jsonify(user), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def login(self):
        try:
            data = request.get_json()
            user = self.user_service.login(
                data.get('username'),
                data.get('password')
            )
            return jsonify(user), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 401

    @require_jwt
    def get_user(self, user_id):
        try:
            user = self.user_service.get_user(user_id)
            if user:
                return jsonify(user), 200
            return jsonify({"error": "User not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    @require_jwt
    def get_user_info(self):
        try:
            user_id = request.user['user_id']
            user = self.user_service.get_user(user_id)
            if user:
                return jsonify(user), 200
            return jsonify({"error": "User not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400
          
    @require_jwt
    def update_user(self, user_id):
        try:
            data = request.get_json()
            user = self.user_service.update_user(
                user_id,
                data.get('username'),
                data.get('email'),
                data.get('full_name'),
                data.get('role')
            )
            if user:
                return jsonify(user), 200
            return jsonify({"error": "User not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def delete_user(self, user_id):
        try:
            success = self.user_service.delete_user(user_id)
            if success:
                return jsonify({"message": "User deleted successfully"}), 200
            return jsonify({"error": "User not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
    @require_jwt
    def get_inspection_guides(self):
        try:
            guides = self.user_service.get_inspection_guides()
            return jsonify(guides), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

   

    def google_login(self):
        data = request.json
        token = data.get('token')

        try:
            # 1. Verify Google Token
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
            email = idinfo['email']
            full_name = idinfo.get('name')

            # 2. Try to find the user in your database
            user = self.user_service.get_user_by_email(email)

            if not user:
                # 3. New User: create_user handles insertion + JWT generation
                username = email.split('@')[0]
                password = os.urandom(16).hex()
                
                # This returns the full dict including the 'token' key
                response_data = self.user_service.create_user(
                    username=username,
                    password=password,
                    email=email,
                    full_name=full_name,
                    role='customer'
                )
            else:
                # 4. Returning User: We must manually generate the token
                auth_token = self.user_service._generate_jwt(
                    user['user_id'], 
                    user['username'], 
                    user['role']
                )
                # Add the token to the user dict so the frontend can find it
                user['token'] = auth_token
                response_data = user

            # 5. Return the token at the top level so handleRoleRouting(response.data.token) works
            return jsonify({
                "message": "Login successful",
                "token": response_data.get('token'),
                "user": response_data
            }), 200

        except ValueError:
            return jsonify({"error": "Invalid Google token"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500