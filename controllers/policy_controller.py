from flask import Blueprint, request, jsonify
from services.policy_service import PolicyService
from middleware.auth import require_jwt
import os

policy_bp = Blueprint('policy', __name__)

class PolicyController:
    def __init__(self, db_config):
        self.policy_service = PolicyService(db_config)

    @require_jwt
    def create_policy_type(self):
        try:
            data = request.get_json()
            user_role = request.user['role']
            policy_type = self.policy_service.create_policy_type(
                data.get('name'),
                data.get('description'),
                data.get('image'),
                user_role
            )
            return jsonify(policy_type), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def get_policy_type(self, policy_type_id):
        try:
            policy_type = self.policy_service.get_policy_type(policy_type_id)
            if policy_type:
                return jsonify(policy_type), 200
            return jsonify({"error": "Policy type not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def get_all_policy_types(self):
        try:
            policy_types = self.policy_service.get_all_policy_types()
            return jsonify(policy_types), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def update_policy_type(self, policy_type_id):
        try:
            data = request.get_json()
            user_role = request.user['role']
            policy_type = self.policy_service.update_policy_type(
                policy_type_id,
                data.get('name'),
                data.get('description'),
                data.get('image'),
                user_role
            )
            if policy_type:
                return jsonify(policy_type), 200
            return jsonify({"error": "Policy type not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def delete_policy_type(self, policy_type_id):
        try:
            user_role = request.user['role']
            success = self.policy_service.delete_policy_type(policy_type_id, user_role)
            if success:
                return jsonify({"message": "Policy type deleted successfully"}), 200
            return jsonify({"error": "Policy type not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def create_policy(self):
        try:
            data = request.get_json()
            user_role = request.user['role']
            user_id = request.user['user_id']
            policy = self.policy_service.create_policy(
                data.get('policy_name'),
                data.get('policy_number'),
                data.get('policy_type_id'),
                data.get('price'),
                data.get('time_period'),
                data.get('start_date'),
                data.get('end_date'),
                data.get('coverage_details'),
                data.get('is_claimable', False),
                data.get('required_documents_count', 0),
                data.get('documents_list'),
                data.get('requires_inspection', False),
                data.get('inspection_checklist'),
                user_id,
                user_role
            )
            return jsonify(policy), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def get_policy(self, policy_id):
        try:
            policy = self.policy_service.get_policy(policy_id)
            if policy:
                return jsonify(policy), 200
            return jsonify({"error": "Policy not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def get_all_policies(self):
        try:
            available_only = request.args.get('available_only', 'false').lower() == 'true'
            policies = self.policy_service.get_all_policies(available_only=available_only)
            return jsonify(policies), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def get_policies_by_customer(self):
        try:
            customer_id = request.user['user_id']
            policies = self.policy_service.get_policies_by_customer(customer_id)
            return jsonify(policies), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def get_policies_by_created_by(self, created_by):
        try:
            policies = self.policy_service.get_policies_by_created_by(created_by)
            return jsonify(policies), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def purchase_policy(self, policy_id):
        try:
            user_role = request.user['role']
            customer_id = request.user['user_id']
            policy = self.policy_service.purchase_policy(policy_id, customer_id, user_role)
            if policy:
                return jsonify(policy), 200
            return jsonify({"error": "Policy not found or already purchased by this customer"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def update_policy(self, policy_id):
        try:
            data = request.get_json()
            user_role = request.user['role']
            policy = self.policy_service.update_policy(
                policy_id,
                data.get('policy_name'),
                data.get('policy_number'),
                data.get('price'),
                data.get('time_period'),
                data.get('start_date'),
                data.get('end_date'),
                data.get('coverage_details'),
                data.get('is_claimable'),
                data.get('required_documents_count'),
                data.get('documents_list'),
                data.get('requires_inspection'),
                data.get('inspection_checklist'),
                user_role
            )
            if policy:
                return jsonify(policy), 200
            return jsonify({"error": "Policy not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def delete_policy(self, policy_id):
        try:
            user_role = request.user['role']
            success = self.policy_service.delete_policy(policy_id, user_role)
            if success:
                return jsonify({"message": "Policy deleted successfully"}), 200
            return jsonify({"error": "Policy not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400