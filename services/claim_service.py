from models.claim_model import ClaimModel
from models.policy_model import PolicyModel

import json
import psycopg2

class ClaimService:
    def __init__(self, db_config):
        self.claim_model = ClaimModel(db_config)
        self.policy_model = PolicyModel(db_config)
     

    def create_claim(self, customer_id, policy_id, user_role):
        if user_role != 'customer':
            raise ValueError("Only customers can create claims")
        policy = self.policy_model.get_policy_by_id(policy_id)
        if not policy:
            raise ValueError("Policy not found")
      
        customer_policies = self.policy_model.get_policies_by_customer(customer_id)
        if not any(p['policy_id'] == policy_id for p in customer_policies):
            raise ValueError("Customer has not purchased this policy")
        try:
            return self.claim_model.create_claim(customer_id, policy_id)
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def upload_claim_document(self, claim_id, document_url, document_type, user_role, customer_id):
        if user_role != 'customer':
            raise ValueError("Only customers can upload claim documents")
        try:
            claims = self.claim_model.get_claims_by_customer(customer_id)
            claim = next((c for c in claims if c['claim_id'] == claim_id), None)
            if not claim:
                raise ValueError("Claim not found")
            if claim['status'] not in ['pending', 'documents_submitted']:
                raise ValueError("Cannot upload documents for this claim status")
            policy = self.policy_model.get_policy_by_id(claim['policy_id'])
            if policy['documents_list'] and document_type not in policy['documents_list']:
                raise ValueError(f"Document type must be one of: {', '.join(policy['documents_list'])}")
            documents = self.claim_model.get_claim_documents(claim_id)
            if len(documents) >= policy['required_documents_count']:
                raise ValueError("Required document count already met")
            document = self.claim_model.upload_claim_document(claim_id, document_url, document_type)
            if len(documents) + 1 == policy['required_documents_count']:
                self.claim_model.update_claim_status(claim_id, 'documents_submitted', None)
            return document
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def schedule_inspection(self, claim_id, inspection_date, inspection_guide_id, user_role):
        if user_role != 'customer':
            raise ValueError("Only customers can schedule inspections")
        try:
            # Fetch claim details to get policy_id
            claim = self.claim_model.get_claim_by_id(claim_id)
            if not claim:
                raise ValueError("Claim not found")
            
            # Fetch policy details using policy_id
            policy = self.policy_model.get_policy_by_id(claim['policy_id'])
            if not policy:
                raise ValueError("Policy not found")
            if not policy['requires_inspection']:
                raise ValueError("Policy does not require inspection")
            
            # Optionally, verify document count
            claim_documents = self.claim_model.get_claim_documents(claim_id)
            if len(claim_documents) < policy['required_documents_count']:
                raise ValueError("All required documents must be submitted before scheduling inspection")
            
            return self.claim_model.schedule_inspection(claim_id, inspection_date, inspection_guide_id)
        except Exception as e:
            raise Exception(f"Service error: {e}")
    def submit_inspection_report(self, appointment_id, inspection_report, user_role, user_id):
        if user_role != 'inspection_guide':
            raise ValueError("Only inspection guides can submit reports")
        try:
            appointments = self.claim_model.get_inspection_appointments_by_id(appointment_id)
            appointment = next((a for a in appointments if a['appointment_id'] == appointment_id and a['inspection_guide_id'] == user_id), None)
            if not appointment:
                raise ValueError("Invalid appointment or unauthorized")
            result = self.claim_model.submit_inspection_report(appointment_id, inspection_report)
            self.claim_model.update_claim_status(appointment['claim_id'], 'inspected',None )
            return result
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def update_claim_status_for_officer(self, claim_id, status, approved_amount, comments,claims_officer_id):
       
        if status not in ['approved', 'declined']:
            raise ValueError("Invalid status")
        try:
            claims = self.claim_model.get_claims_by_officer(claims_officer_id)
            claim = next((c for c in claims if c['claim_id'] == claim_id), None)
            if not claim:
                raise ValueError("Claim not assigned to this officer")
            policy = self.policy_model.get_policy_by_id(claim['policy_id'])
            if policy['requires_inspection'] and claim['status'] != 'inspected':
                raise ValueError("Claim must be inspected before approval/decline")
            return self.claim_model.update_claim_status_for_officer( claim_id, status, approved_amount, comments,claims_officer_id)
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def get_claims_by_customer(self, customer_id, user_role):
        if user_role != 'customer':
            raise ValueError("Only customers can view their claims")
        try:
            return self.claim_model.get_claims_by_customer(customer_id)
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def get_claims_by_inspection_guide(self, inspection_guide_id, user_role):
        if user_role != 'inspection_guide':
            raise ValueError("Only inspection guides can view their claims")
        try:
            return self.claim_model.get_claims_by_inspection_guide(inspection_guide_id)
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def get_claims_by_officer(self, claims_officer_id, user_role):
        if user_role != 'claims_officer':
            raise ValueError("Only claims officers can view their claims")
        try:
            return self.claim_model.get_claims_by_officer(claims_officer_id)
        except Exception as e:
            raise Exception(f"Service error: {e}")

    def get_policy_checklist(self, policy_id):
        try:
            policy = self.policy_model.get_policy_by_id(policy_id)
            if not policy:
                raise ValueError("Policy not found")
            return policy['inspection_checklist'] or []
        except Exception as e:
            raise Exception(f"Service error: {e}")
        
    def get_policies_with_claim_counts(self, user_id):
        try:
            return self.policy_model.get_policies_with_claim_counts(user_id)
        except Exception as e:
            raise Exception(f"Service error: {e}")
    def get_claim_details_for_officer(self,claim_id):
        try: 
            return self.claim_model.get_claim_by_id(claim_id)
        except Exception as e:
            raise Exception(f"Service error: {e}")
        
    def  get_documents_by_claim_id(self,claim_id):
        try:
            return self.claim_model.get_documents_by_claim_id(claim_id)
        except Exception as e:
            raise Exception(f"Service error: {e}")
   
    def get_appointment_by_id(self, appointment_id):
        try:
            return self.claim_model.get_appointment_by_id(appointment_id)
        except Exception as e:
            raise Exception(f"Service error: {e}")
    def update_inspection_report(self, appointment_id, inspection_report):
        try:
            return self.claim_model.update_inspection_report(appointment_id, inspection_report)
        except Exception as e:
            raise Exception(f"Service error: {e}")
        
    def update_appointment_status(self, appointment_id, status):
        try:
            return self.claim_model.update_appointment_status(appointment_id, status)
        except Exception as e:
            raise Exception(f"Service error: {e}")