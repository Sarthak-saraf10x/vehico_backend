from flask import Flask,send_from_directory
from flask_cors import CORS
from controllers.user_controller import UserController, user_bp
from controllers.policy_controller import PolicyController,policy_bp
from controllers.claim_controller import ClaimController,claim_bp

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)
# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "http://localhost:5173",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Database configuration
db_config = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Initialize controller
user_controller = UserController(db_config)
policy_controller = PolicyController(db_config)
claim_controller = ClaimController(db_config)


# user routs
user_bp.route('/', methods=['POST'])(user_controller.create_user)
user_bp.route('/login', methods=['POST'])(user_controller.login)
user_bp.route('/<user_id>', methods=['GET'])(user_controller.get_user)
user_bp.route('/<user_id>', methods=['PUT'])(user_controller.update_user)
user_bp.route('/<user_id>', methods=['DELETE'])(user_controller.delete_user)
user_bp.route('/me', methods=['GET'])(user_controller.get_user_info)
user_bp.route('/inspection_guides', methods=['GET'])(user_controller.get_inspection_guides)
user_bp.route('/google-login', methods=['POST'])(user_controller.google_login)

# Policy routes
policy_bp.route('/types', methods=['POST'])(policy_controller.create_policy_type)
policy_bp.route('/types/<policy_type_id>', methods=['GET'])(policy_controller.get_policy_type)
policy_bp.route('/types', methods=['GET'])(policy_controller.get_all_policy_types)
policy_bp.route('/types/<policy_type_id>', methods=['PUT'])(policy_controller.update_policy_type)
policy_bp.route('/types/<policy_type_id>', methods=['DELETE'])(policy_controller.delete_policy_type)
policy_bp.route('/', methods=['POST'])(policy_controller.create_policy)
policy_bp.route('/', methods=['GET'])(policy_controller.get_all_policies)
policy_bp.route('/created_by/<created_by>', methods=['GET'])(policy_controller.get_policies_by_created_by)
policy_bp.route('/<policy_id>', methods=['GET'])(policy_controller.get_policy)
policy_bp.route('/<policy_id>', methods=['PUT'])(policy_controller.update_policy)
policy_bp.route('/<policy_id>', methods=['DELETE'])(policy_controller.delete_policy)
policy_bp.route('/<policy_id>/purchase', methods=['POST'])(policy_controller.purchase_policy)
policy_bp.route('/customer', methods=['GET'])(policy_controller.get_policies_by_customer)


# Claim routes
claim_bp.route('/', methods=['POST'])(claim_controller.create_claim)
claim_bp.route('/<claim_id>/documents', methods=['POST'])(claim_controller.upload_claim_document) 
claim_bp.route('/<claim_id>/inspection', methods=['POST'])(claim_controller.schedule_inspection)
claim_bp.route('/<appointment_id>/inspection/report', methods=['POST'])(claim_controller.submit_inspection_report)
claim_bp.route('/<claim_id>', methods=['GET'])(claim_controller.get_claim_details) 
claim_bp.route('/<claim_id>', methods=['PUT'])(claim_controller.update_claim_status)
claim_bp.route('/customer', methods=['GET'])(claim_controller.get_claims_by_customer)
claim_bp.route('/inspection_guide', methods=['GET'])(claim_controller.get_claims_by_inspection_guide)

policy_bp.route('/<policy_id>/checklist', methods=['GET'])(claim_controller.get_policy_checklist)
policy_bp.route('/<user_id>/claims', methods=['GET'])(claim_controller.get_policies_with_claims)
claim_bp.route('/officer', methods=['GET'])(claim_controller.get_claims_for_officer)
claim_bp.route('/officer/<claim_id>', methods=['GET'])(claim_controller.get_claim_details_for_officer)
claim_bp.route('/<claim_id>/approve', methods=['POST'])(claim_controller.approve_claim)



# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(policy_bp, url_prefix='/api/policies')
app.register_blueprint(claim_bp, url_prefix='/api/claims')

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)


if __name__ == '__main__':
    app.run(debug=True)