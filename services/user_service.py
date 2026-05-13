import jwt
import datetime
import os
from models.user_model import UserModel
import bcrypt

class UserService:
    def __init__(self, db_config):
        self.user_model = UserModel(db_config)
        self.jwt_secret = os.getenv("JWT_SECRET_KEY")
        self.jwt_expires = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))  # Default to 1 hour if not set
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET_KEY is not set in environment variables")

    def create_user(self, username, password, email, full_name, role):
        if not all([username, password, email, full_name, role]):
            raise ValueError("All fields are required")
        if role not in ['customer', 'claims_officer', 'admin', 'policy_manager']:
            raise ValueError("Invalid role")
        try:
            user = self.user_model.create_user(username, password, email, full_name, role)
            token = self._generate_jwt(user[0], username, role)
            return {
                "user_id": str(user[0]),
                "username": user[1],
                "email": user[2],
                "full_name": user[3],
                "role": user[4],
                "created_at": user[5].isoformat(),
                "updated_at": user[6].isoformat(),
                "token": token
            }
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def login(self, username, password):
        try:
            user = self.user_model.get_user_by_username(username)
            if not user:
                raise ValueError("User not found")
            if bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                token = self._generate_jwt(user[0], user[1], user[5])
                return {
                    "user_id": str(user[0]),
                    "username": user[1],
                    "email": user[3],
                    "full_name": user[4],
                    "role": user[5],
                    "created_at": user[6].isoformat(),
                    "updated_at": user[7].isoformat(),
                    "token": token
                }
            else:
                raise ValueError("Invalid password")
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def _generate_jwt(self, user_id, username, role):
        payload = {
            "user_id": str(user_id),
            "username": username,
            "role": role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=self.jwt_expires),
            "iat": datetime.datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def get_user(self, user_id):
        try:
            user = self.user_model.get_user_by_id(user_id)
            if user:
                return {
                    "user_id": str(user[0]),
                    "username": user[1],
                    "email": user[2],
                    "full_name": user[3],
                    "role": user[4],
                    "created_at": user[5].isoformat(),
                    "updated_at": user[6].isoformat()
                }
            return None
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def update_user(self, user_id, username=None, email=None, full_name=None, role=None):
        try:
            user = self.user_model.update_user(user_id, username, email, full_name, role)
            if user:
                return {
                    "user_id": str(user[0]),
                    "username": user[1],
                    "email": user[2],
                    "full_name": user[3],
                    "role": user[4],
                    "created_at": user[5].isoformat(),
                    "updated_at": user[6].isoformat()
                }
            return None
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def delete_user(self, user_id):
        try:
            success = self.user_model.delete_user(user_id)
            return success
        except Exception as e:
            raise Exception(f"Service error: {e}")
        
    def get_inspection_guides(self):
        try:
            return self.user_model.get_inspection_guides()
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def get_user_by_email(self, email):
        try:
            # You'll need to implement this method in your UserModel class first
            user = self.user_model.get_user_by_email(email)
            if user:
                return {
                    "user_id": str(user[0]),
                    "username": user[1],
                    # user[2] is likely the hashed password, skip it
                    "email": user[2],
                    "full_name": user[3],
                    "role": user[4],
                    "created_at": user[5].isoformat(),
                    "updated_at": user[6].isoformat()
                }
            return None
        except Exception as e:
            raise Exception(f"Service error: {e}")