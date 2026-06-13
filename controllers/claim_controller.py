from flask import Blueprint, request, jsonify
from services.claim_service import ClaimService
from services.policy_service import PolicyService
from models.claim_model import ClaimModel
from models.policy_model import PolicyModel
from models.claim_document_model import ClaimDocumentModel
from models.inspection_appointment_model import InspectionAppointmentModel
from commons.db_handler import DatabaseHandler
from middleware.auth import require_jwt
from flask import send_from_directory
import os
import uuid
import json

claim_bp = Blueprint('claim', __name__)

class ClaimController:
    def __init__(self, db_config):
       
        self.claim_service = ClaimService(db_config)
        self.claim_model = ClaimModel(db_config)
        self.policy_service = PolicyService(db_config)
     
      
       
        self.upload_dir = 'uploads'
        os.makedirs(self.upload_dir, exist_ok=True)

    @require_jwt
    def create_claim(self):
        try:
            data = request.get_json()
            customer_id = request.user['user_id']
            user_role = request.user['role']
            policy_id = data.get('policy_id')
            if not policy_id:
                return jsonify({"error": "Policy ID is required"}), 400
            claim = self.claim_service.create_claim(customer_id, policy_id, user_role)
            return jsonify(claim), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def upload_claim_document(self, claim_id):
        try:
            user_role = request.user['role']
            customer_id = request.user['user_id']
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400
            file = request.files['file']
            document_type = request.form.get('document_type')
            if not document_type:
                return jsonify({"error": "Document type is required"}), 400
            if not file.filename:
                return jsonify({"error": "No file selected"}), 400
            
            allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({"error": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"}), 400
            
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            file.save(file_path)
            
            file_url = f"http://localhost:5000/uploads/{unique_filename}"
            
            document = self.claim_service.upload_claim_document(claim_id, file_url, document_type, user_role, customer_id)
            return jsonify(document), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def schedule_inspection(self, claim_id):
        try:
            data = request.get_json()
            user_role = request.user['role']
           
            inspection_date = data.get('inspection_date')
            inspection_guide_id = data.get('inspection_guide_id')
            if not inspection_date:
                return jsonify({"error": "Inspection date is required"}), 400
            appointment = self.claim_service.schedule_inspection(claim_id, inspection_date, inspection_guide_id, user_role)
            return jsonify(appointment), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def submit_inspection_report(self, appointment_id):
        try:
            user_role = request.user['role']
            user_id = request.user['user_id']
            if user_role != 'inspection_guide':
                return jsonify({"error": "Only inspection guides can submit reports"}), 403

            # Validate appointment
           # appointment = self.appointment_model.get_appointment_by_id(appointment_id)
            appointment = self.claim_service.get_appointment_by_id(appointment_id)
            if not appointment:
                return jsonify({"error": "Appointment not found"}), 404
            if appointment['status'] != 'scheduled':
                return jsonify({"error": "Appointment is not in scheduled status"}), 400

            # Validate claim
            claim = self.claim_model.get_claim_by_id(appointment['claim_id'])
            if not claim:
                return jsonify({"error": "Claim not found"}), 404
            if claim['status'] != 'inspection_scheduled':
                return jsonify({"error": "Claim is not pending inspection"}), 400

            # Handle file upload
            image_url = None
            if 'file' in request.files:
                file = request.files['file']
                if not file.filename:
                    return jsonify({"error": "No file selected"}), 400
                allowed_extensions = {'.jpg', '.jpeg', '.png'}
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext not in allowed_extensions:
                    return jsonify({"error": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"}), 400
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                report_dir = os.path.join(self.upload_dir, 'inspection_reports')
                os.makedirs(report_dir, exist_ok=True)
                file_path = os.path.join(report_dir, unique_filename)
                file.save(file_path)
                image_url = f"http://localhost:5000/uploads/inspection_reports/{unique_filename}"

            # Get form data
            data = request.form
            checklist_responses = data.get('checklist_responses')
            comments = data.get('comments')
            if not checklist_responses:
                return jsonify({"error": "Checklist responses are required"}), 400

            # Parse checklist_responses and create inspection report
            inspection_report = {
                'checklist_responses': json.loads(checklist_responses) if checklist_responses else {},
                'comments': comments,
                'image_url': image_url
            }

            # Update database
            self.claim_service.update_inspection_report(appointment_id, inspection_report)
            self.claim_service.update_appointment_status(appointment_id, 'completed')
            self.claim_model.update_claim_status(appointment['claim_id'], 'inspected')

            # Fetch updated appointment for response
            updated_appointment = self.claim_service.get_appointment_by_id(appointment_id)
            return jsonify(updated_appointment), 200
        except Exception as e:
            return jsonify({"error": f"Failed to submit inspection report: {str(e)}"}), 400


    @require_jwt
    def update_claim_status(self, claim_id):
        try:
            data = request.get_json()
            user_role = request.user['role']
            user_id = request.user['user_id']
            status = data.get('status')
            comments = data.get('comments')
            if not status:
                return jsonify({"error": "Status is required"}), 400
            claim = self.claim_service.update_claim_status(claim_id, status, user_role, user_id, comments)
            return jsonify(claim), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def get_claims_by_customer(self):
        try:
            customer_id = request.user['user_id']
            user_role = request.user['role']
            claims = self.claim_service.get_claims_by_customer(customer_id, user_role)
            return jsonify(claims), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def get_claims_by_inspection_guide(self):
        try:
            inspection_guide_id = request.user['user_id']
            user_role = request.user['role']
            claims = self.claim_service.get_claims_by_inspection_guide(inspection_guide_id, user_role)
            return jsonify(claims), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    @require_jwt
    def get_assigned_claims(self, user_id):
        try:
           
            user_id = request.user['user_id']
            user_role = request.user['role']
            claims = self.claim_service.get_assigned_claims(user_id, user_role)
            return jsonify(claims), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
    @require_jwt
    def get_claims_by_officer(self):
        try:
            claims_officer_id = request.user['user_id']
            user_role = request.user['role']
            claims = self.claim_service.get_claims_by_officer(claims_officer_id, user_role)
            return jsonify(claims), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def get_claim_details(self, claim_id):
        try:
            user_role = request.user['role']
            user_id = request.user['user_id']
            claims = []
            if user_role == 'customer':
                claims = self.claim_service.get_claims_by_customer(user_id, user_role)
            elif user_role == 'inspection_guide':
                claims = self.claim_service.get_claims_by_inspection_guide(user_id, user_role)
            elif user_role == 'claims_officer':
                claims = self.claim_service.get_claims_by_officer(user_id, user_role)
            else:
                return jsonify({"error": "Unauthorized role"}), 403
            claim = next((c for c in claims if c['claim_id'] == claim_id), None)
            if not claim:
                return jsonify({"error": "Claim not found or unauthorized"}), 404
            documents = self.claim_service.claim_model.get_claim_documents(claim_id)
            appointments = self.claim_service.claim_model.get_inspection_appointments(claim_id)
            return jsonify({
                "claim": claim,
                "documents": documents,
                "appointments": appointments
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @require_jwt
    def get_policy_checklist(self, policy_id):
        try:
            user_role = request.user['role']
            if user_role != 'inspection_guide':
                return jsonify({"error": "Only inspection guides can access checklists"}), 403
            checklist = self.claim_service.get_policy_checklist(policy_id)
            return jsonify(checklist), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400 
    def get_policies_with_claims(self, user_id):
        try:
            policies = self.claim_service.get_policies_with_claim_counts(user_id)
          #  policies = self.policy_model.get_policies_with_claim_counts(claim_manager_id)
            return jsonify(policies), 200
        except Exception as e:
            return jsonify({"error": f"Failed to fetch policies: {str(e)}"}), 500

    def get_claims_for_officer(self):
        try:
            claims = self.claim_model.get_claims_with_inspection_status()
            return jsonify(claims), 200
        except Exception as e:
            return jsonify({"error": f"Failed to fetch claims: {str(e)}"}), 500

    def get_claim_details_for_officer(self, claim_id):
        
        try:
            claim = self.claim_model.get_claim_by_id(claim_id)
            if not claim:
                return jsonify({"error": "Claim not found"}), 404
            policy = self.policy_service.get_policy(claim['policy_id'])

            appointment = self.claim_service.get_claim_details_for_officer(claim_id)
            documents = self.claim_service.get_documents_by_claim_id(claim_id)
          
            return jsonify({
                "claim": claim,
                "policy": policy,
                "inspection_appointment": appointment,
                "documents": documents
            }), 200
        except Exception as e:
            return jsonify({"error": f"Failed to fetch claim details: {str(e)}"}), 500

    @require_jwt
    def approve_claim(self, claim_id):
        try:
            claims_officer_id = request.user['user_id']
            data = request.get_json()
            status = data.get('status') 
            approved_amount = data.get('approved_amount', 0)
            if approved_amount == "":
                approved_amount = 0
            comments = data.get('comments', None)
            

            if status not in ['approved', 'rejected']:
                return jsonify({"error": "Invalid status"}), 400
            if status == 'approved' and (approved_amount is None or float(approved_amount) <= 0):
                return jsonify({"error": "Valid approved amount required for approval"}), 400

            claim = self.claim_model.get_claim_by_id(claim_id)
            if not claim:   
                return jsonify({"error": "Claim not found"}), 404
            if claim['status'] != 'inspected':
                return jsonify({"error": "Claim is not ready for approval"}), 400
            

            self.claim_model. update_claim_status_for_officer(claim_id, status, approved_amount, comments,claims_officer_id)
            return jsonify({"message": f"Claim {status} successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to process claim: {str(e)}"}), 500
@claim_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    exact_path = os.path.join('uploads', filename)
    if os.path.exists(exact_path) and os.path.isfile(exact_path):
        return send_from_directory('uploads', filename)
    
    base_name = os.path.basename(filename)
    root_path = os.path.join('uploads', base_name)
    if os.path.exists(root_path) and os.path.isfile(root_path):
        return send_from_directory('uploads', base_name)
        
    return "File not found", 404

