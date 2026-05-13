import bcrypt
from commons.db_handler import DatabaseHandler

class UserModel:
    def __init__(self, db_config):
        self.db_handler = DatabaseHandler(**db_config)

    def create_user(self, username, password, email, full_name, role):
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query = """
            INSERT INTO users (username, password_hash, email, full_name, role)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id, username, email, full_name, role, created_at, updated_at
        """
        try:
            result = self.db_handler.execute_query(query, (username, password_hash, email, full_name, role), fetch=True)
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Failed to create user: {e}")

    def get_user_by_id(self, user_id):
        query = """
            SELECT user_id, username, email, full_name, role, created_at, updated_at
            FROM users
            WHERE user_id = %s
        """
        try:
            result = self.db_handler.execute_query(query, (user_id,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Failed to get user: {e}")

    def get_user_by_username(self, username):
        query = """
            SELECT user_id, username, password_hash, email, full_name, role, created_at, updated_at
            FROM users
            WHERE username = %s
        """
        try:
            result = self.db_handler.execute_query(query, (username,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Failed to get user by username: {e}")
    def get_user_by_email(self, email):
        query = """
            SELECT user_id, username, email, full_name, role, created_at, updated_at
            FROM users
            WHERE email = %s
        """
        try:
            result = self.db_handler.execute_query(query, (email,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Failed to get user by email: {e}")
    def update_user(self, user_id, username=None, email=None, full_name=None, role=None):
        updates = []
        params = []
        if username:
            updates.append("username = %s")
            params.append(username)
        if email:
            updates.append("email = %s")
            params.append(email)
        if full_name:
            updates.append("full_name = %s")
            params.append(full_name)
        if role:
            updates.append("role = %s")
            params.append(role)
        
        if not updates:
            raise Exception("No fields to update")
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        query = f"""
            UPDATE users
            SET {', '.join(updates)}
            WHERE user_id = %s
            RETURNING user_id, username, email, full_name, role, created_at, updated_at
        """
        try:
            result = self.db_handler.execute_query(query, tuple(params), fetch=True)
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Failed to update user: {e}")

    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE user_id = %s"
        try:
            self.db_handler.execute_query(query, (user_id,))
            return True
        except Exception as e:
            raise Exception(f"Failed to delete user: {e}")
        
    def get_inspection_guides(self):
        query = """
            SELECT user_id, username
            FROM users
            WHERE role = 'inspection_guide'
        """
        try:
            results = self.db_handler.execute_query(query, fetch=True)
            return [
                {
                    "user_id": str(row[0]),
                    "name": row[1]
                }
                for row in results
            ] if results else []
        except Exception as e:
            raise Exception(f"Failed to get inspection guides: {e}")