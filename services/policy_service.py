from models.policy_model import PolicyModel
from datetime import datetime
import json
import psycopg2

class PolicyService:
    def __init__(self, db_config):
        self.policy_model = PolicyModel(db_config)

    def create_policy_type(self, name, description, image, user_role):
        if user_role != 'policy_manager':
            raise ValueError("Only policy_manager can create policy types")
        if not name:
            raise ValueError("Policy type name is required")
        try:
            policy_type = self.policy_model.create_policy_type(name, description, image)
            return policy_type
        except psycopg2.errors.UniqueViolation:
            raise ValueError("Policy type name already exists")
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def get_policy_type(self, policy_type_id):
        try:
            policy_type = self.policy_model.get_policy_type_by_id(policy_type_id)
            return policy_type
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def get_all_policy_types(self):
        try:
            policy_types = self.policy_model.get_all_policy_types()
            return policy_types
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def update_policy_type(self, policy_type_id, name, description, image, user_role):
        if user_role != 'policy_manager':
            raise ValueError("Only policy_manager can update policy types")
        try:
            policy_type = self.policy_model.update_policy_type(policy_type_id, name, description, image)
            return policy_type
        except psycopg2.errors.UniqueViolation:
            raise ValueError("Policy type name already exists")
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def delete_policy_type(self, policy_type_id, user_role):
        if user_role != 'policy_manager':
            raise ValueError("Only policy_manager can delete policy types")
        try:
            success = self.policy_model.delete_policy_type(policy_type_id)
            return success
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def create_policy(self, policy_name, policy_number, policy_type_id, price, time_period, start_date, end_date, coverage_details, is_claimable, required_documents_count, documents_list, requires_inspection, inspection_checklist, created_by, user_role):
        if user_role != 'policy_manager':
            raise ValueError("Only policy_manager can create policies")
        if not all([policy_name, policy_number, policy_type_id, price, time_period, start_date, end_date]):
            raise ValueError("Required fields are missing")
        if time_period not in ['one_year', 'two_years']:
            raise ValueError("Invalid time period")
       
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        if not self.policy_model.get_policy_type_by_id(policy_type_id):
            raise ValueError("Invalid policy type ID")
        # Convert required_documents_count to integer
        try:
            required_documents_count = int(required_documents_count) if required_documents_count is not None else 0
        except (ValueError, TypeError):
            raise ValueError("Required documents count must be a valid integer")
        if is_claimable:
            if required_documents_count < 0:
                raise ValueError("Required documents count must be non-negative for claimable policies")
            if documents_list is None or not isinstance(documents_list, list) or len(documents_list) != required_documents_count:
                raise ValueError("Documents list must match required documents count")
            if requires_inspection and (inspection_checklist is None or not isinstance(inspection_checklist, list)):
                raise ValueError("Inspection checklist must be a list for policies requiring inspection")
        else:
            if required_documents_count != 0 or documents_list is not None:
                raise ValueError("Non-claimable policies cannot have documents")
            if requires_inspection or inspection_checklist is not None:
                raise ValueError("Non-claimable policies cannot require inspection")
        try:
            policy = self.policy_model.create_policy(
                policy_name, policy_number, policy_type_id, price, time_period, start_date, end_date, 
                json.dumps(coverage_details), is_claimable, required_documents_count, 
                json.dumps(documents_list) if documents_list else None, 
                requires_inspection, json.dumps(inspection_checklist) if inspection_checklist else None, 
                created_by
            )
            return policy
        except psycopg2.errors.UniqueViolation:
            raise ValueError("Policy number already exists")
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def get_policy(self, policy_id):
        try:
            policy = self.policy_model.get_policy_by_id(policy_id)
            return policy
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def get_all_policies(self, available_only=False):
        try:
            policies = self.policy_model.get_all_policies()
            return policies
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def get_policies_by_customer(self, customer_id):
        try:
            policies = self.policy_model.get_policies_by_customer(customer_id)
            return policies
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def get_policies_by_created_by(self, created_by):
        try:
            policies = self.policy_model.get_policies_by_created_by(created_by)
            return policies
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def purchase_policy(self, policy_id, customer_id, user_role):
        if user_role != 'customer':
            raise ValueError("Only customers can purchase policies")
        try:
            policy = self.policy_model.purchase_policy(policy_id, customer_id)
            if not policy:
                raise ValueError("Policy not found")
            return policy
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def update_policy(self, policy_id, policy_name, policy_number, price, time_period, start_date, end_date, coverage_details, is_claimable, required_documents_count, documents_list, requires_inspection, inspection_checklist, user_role):
        if user_role != 'policy_manager':
            raise ValueError("Only policy_manager can update policies")
        if time_period and time_period not in ['one_year', 'two_years']:
            raise ValueError("Invalid time period")
       
        if start_date and end_date and start_date >= end_date:
            raise ValueError("Start date must be before end date")
        # Convert required_documents_count to integer
        try:
            required_documents_count = int(required_documents_count) if required_documents_count is not None else None
        except (ValueError, TypeError):
            raise ValueError("Required documents count must be a valid integer")
        if is_claimable is not None and is_claimable:
            if required_documents_count is not None and required_documents_count < 0:
                raise ValueError("Required documents count must be non-negative for claimable policies")
            if documents_list is not None and (not isinstance(documents_list, list) or len(documents_list) != required_documents_count):
                raise ValueError("Documents list must match required documents count")
            if requires_inspection is not None and requires_inspection and (inspection_checklist is None or not isinstance(inspection_checklist, list)):
                raise ValueError("Inspection checklist must be a list for policies requiring inspection")
        elif is_claimable is not None:
            if required_documents_count is not None and required_documents_count != 0:
                raise ValueError("Non-claimable policies cannot have documents")
            if documents_list is not None:
                raise ValueError("Non-claimable policies cannot have documents list")
            if requires_inspection is not None and requires_inspection:
                raise ValueError("Non-claimable policies cannot require inspection")
            if inspection_checklist is not None:
                raise ValueError("Non-claimable policies cannot have inspection checklist")
        try:
            policy = self.policy_model.update_policy(
                policy_id, policy_name, policy_number, price, time_period, start_date, end_date, 
                json.dumps(coverage_details) if coverage_details else None,
                is_claimable, required_documents_count, 
                json.dumps(documents_list) if documents_list else None,
                requires_inspection, json.dumps(inspection_checklist) if inspection_checklist else None
            )
            return policy
        except psycopg2.errors.UniqueViolation:
            raise ValueError("Policy number already exists")
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def delete_policy(self, policy_id, user_role):
        if user_role != 'policy_manager':
            raise ValueError("Only policy_manager can delete policies")
        try:
            success = self.policy_model.delete_policy(policy_id)
            return success
        except Exception as e:
            raise Exception(f"Service error: {e}")