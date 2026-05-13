import psycopg2
from commons.db_handler import DatabaseHandler
from datetime import datetime
import json

class ClaimModel:
    def __init__(self, db_config):
        self.db_handler = DatabaseHandler(**db_config)

    def create_claim(self, customer_id, policy_id):
        query = """
            INSERT INTO claims (customer_id, policy_id, claim_date, status)
            VALUES (%s, %s, CURRENT_TIMESTAMP, 'pending')
            RETURNING claim_id, customer_id, policy_id, claim_date, status, inspection_date, 
                      inspection_guide_id, claims_officer_id, comments, created_at, updated_at
        """
        try:
            result = self.db_handler.execute_query(query, (customer_id, policy_id), fetch=True)
            return {
                "claim_id": str(result[0][0]),
                "customer_id": str(result[0][1]),
                "policy_id": str(result[0][2]),
                "claim_date": result[0][3].isoformat() if result[0][3] else None,
                "status": result[0][4],
                "inspection_date": result[0][5].isoformat() if result[0][5] else None,
                "inspection_guide_id": str(result[0][6]) if result[0][6] else None,
                "claims_officer_id": str(result[0][7]) if result[0][7] else None,
                "comments": result[0][8],
                "created_at": result[0][9].isoformat() if result[0][9] else None,
                "updated_at": result[0][10].isoformat() if result[0][10] else None
            } if result else None
        except Exception as e:
            raise Exception(f"Failed to create claim: {e}")

    def upload_claim_document(self, claim_id, document_url, document_type):
        query = """
            INSERT INTO claim_documents (claim_id, document_url, document_type, uploaded_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING document_id, claim_id, document_url, document_type, uploaded_at
        """
        try:
            result = self.db_handler.execute_query(query, (claim_id, document_url, document_type), fetch=True)
            return {
                "document_id": str(result[0][0]),
                "claim_id": str(result[0][1]),
                "document_url": result[0][2],
                "document_type": result[0][3],
                "uploaded_at": result[0][4].isoformat() if result[0][4] else None
            } if result else None
        except Exception as e:
            raise Exception(f"Failed to upload document: {e}")

    def get_claim_documents(self, claim_id):
        query = """
            SELECT document_id, claim_id, document_url, document_type, uploaded_at
            FROM claim_documents
            WHERE claim_id = %s
        """
        try:
            results = self.db_handler.execute_query(query, (claim_id,), fetch=True)
            return [
                {
                    "document_id": str(row[0]),
                    "claim_id": str(row[1]),
                    "document_url": row[2],
                    "document_type": row[3],
                    "uploaded_at": row[4].isoformat() if row[4] else None
                }
                for row in results
            ] if results else []
        except Exception as e:
            raise Exception(f"Failed to get claim documents: {e}")

    def schedule_inspection(self, claim_id, inspection_date, inspection_guide_id):
        query = """
            INSERT INTO inspection_appointments (claim_id, inspection_guide_id, appointment_date, status)
            VALUES (%s, %s, %s, 'scheduled')
            RETURNING appointment_id, claim_id, inspection_guide_id, appointment_date, status, inspection_report, created_at, updated_at
        """
        try:
            result = self.db_handler.execute_query(query, (claim_id, inspection_guide_id, inspection_date), fetch=True)
            self.update_claim_status(claim_id, 'inspection_scheduled')
            return {
                "appointment_id": str(result[0][0]),
                "claim_id": str(result[0][1]),
                "inspection_guide_id": str(result[0][2]) if result[0][2] else None,
                "appointment_date": result[0][3].isoformat() if result[0][3] else None,
                "status": result[0][4],
                "inspection_report": result[0][5],
                "created_at": result[0][6].isoformat() if result[0][6] else None,
                "updated_at": result[0][7].isoformat() if result[0][7] else None
            } if result else None
        except Exception as e:
            raise Exception(f"Failed to schedule inspection: {e}")

    def submit_inspection_report(self, appointment_id, inspection_report):
        query = """
            UPDATE inspection_appointments
            SET inspection_report = %s, status = 'completed', updated_at = CURRENT_TIMESTAMP
            WHERE appointment_id = %s
            RETURNING appointment_id, claim_id, inspection_guide_id, appointment_date, status, inspection_report, created_at, updated_at
        """
        try:
            result = self.db_handler.execute_query(query, (json.dumps(inspection_report), appointment_id), fetch=True)
            claim_id = str(result[0][1])
            self.update_claim_status(claim_id, 'inspected', None)
            return {
                "appointment_id": str(result[0][0]),
                "claim_id": claim_id,
                "inspection_guide_id": str(result[0][2]) if result[0][2] else None,
                "appointment_date": result[0][3].isoformat() if result[0][3] else None,
                "status": result[0][4],
                "inspection_report": result[0][5],
                "created_at": result[0][6].isoformat() if result[0][6] else None,
                "updated_at": result[0][7].isoformat() if result[0][7] else None
            } if result else None
        except Exception as e:
            raise Exception(f"Failed to submit inspection report: {e}")

    def update_claim_status_for_officer(self, claim_id, status, approved_amount, comments,claims_officer_id):
        updates = ["status = %s", "updated_at = CURRENT_TIMESTAMP"]
        params = [status]
        if claims_officer_id:
            updates.append("claims_officer_id = %s")    
            params.append(claims_officer_id)
        if comments is not None:
            updates.append("comments = %s")
            params.append(comments)
        if approved_amount is not None:
            updates.append("approved_amount = %s")
            params.append(approved_amount)
        params.append(claim_id)
        query = f"""
            UPDATE claims
            SET {', '.join(updates)}
            WHERE claim_id = %s
            RETURNING claim_id, customer_id, policy_id, claim_date, status, inspection_date, 
                      inspection_guide_id, claims_officer_id, comments, created_at,updated_at,approved_amount
        """
        try:
            result = self.db_handler.execute_query(query, tuple(params), fetch=True)
            return {
                "claim_id": str(result[0][0]),
                "customer_id": str(result[0][1]),
                "policy_id": str(result[0][2]),
                "claim_date": result[0][3].isoformat() if result[0][3] else None,
                "status": result[0][4],
                "inspection_date": result[0][5].isoformat() if result[0][5] else None,
                "inspection_guide_id": str(result[0][6]) if result[0][6] else None,
                "claims_officer_id": str(result[0][7]) if result[0][7] else None,
                "comments": result[0][8],
                "created_at": result[0][9].isoformat() if result[0][9] else None,
                "updated_at": result[0][10].isoformat() if result[0][10] else None,
                "approved_amount": float(result[0][11]) if result[0][11] is not None else None
            } if result else None
        except Exception as e:
            raise Exception(f"Failed to update claim status: {e}")

    def get_claims_by_customer(self, customer_id):
        query = """
            SELECT claim_id, customer_id, policy_id, claim_date, status, inspection_date, 
                   inspection_guide_id, claims_officer_id, comments, created_at, updated_at
            FROM claims
            WHERE customer_id = %s
        """
        try:
            results = self.db_handler.execute_query(query, (customer_id,), fetch=True)
            return [
                {
                    "claim_id": str(row[0]),
                    "customer_id": str(row[1]),
                    "policy_id": str(row[2]),
                    "claim_date": row[3].isoformat() if row[3] else None,
                    "status": row[4],
                    "inspection_date": row[5].isoformat() if row[5] else None,
                    "inspection_guide_id": str(row[6]) if row[6] else None,
                    "claims_officer_id": str(row[7]) if row[7] else None,
                    "comments": row[8],
                    "created_at": row[9].isoformat() if row[9] else None,
                    "updated_at": row[10].isoformat() if row[10] else None,
                   # "approved_amount": row[11].isoformat() if row[11] else None
                }
                for row in results
            ] if results else []
        except Exception as e:
            raise Exception(f"Failed to get claims by customer: {e}")

    def get_claims_by_inspection_guide(self, inspection_guide_id):
        query = """
            SELECT c.claim_id, c.customer_id, c.policy_id, c.claim_date, c.status, c.inspection_date, 
                   c.inspection_guide_id, c.claims_officer_id, c.comments, c.created_at, c.updated_at,c.approved_amount
            FROM claims c
            JOIN inspection_appointments ia ON c.claim_id = ia.claim_id
            WHERE ia.inspection_guide_id = %s
        """
        try:
            results = self.db_handler.execute_query(query, (inspection_guide_id,), fetch=True)
            return [
                {
                    "claim_id": str(row[0]),
                    "customer_id": str(row[1]),
                    "policy_id": str(row[2]),
                    "claim_date": row[3].isoformat() if row[3] else None,
                    "status": row[4],
                    "inspection_date": row[5].isoformat() if row[5] else None,
                    "inspection_guide_id": str(row[6]) if row[6] else None,
                    "claims_officer_id": str(row[7]) if row[7] else None,
                    "comments": row[8],
                    "created_at": row[9].isoformat() if row[9] else None,
                    "updated_at": row[10].isoformat() if row[10] else None,
                    "approved_amount": float(row[11]) if row[11] is not None else 0.0

                }
                for row in results
            ] if results else []
        except Exception as e:
            raise Exception(f"Failed to get claims by inspection guide: {e}")

    def get_claims_by_officer(self, claims_officer_id):
        query = """
            SELECT claim_id, customer_id, policy_id, claim_date, status, inspection_date, 
                   inspection_guide_id, claims_officer_id, comments, created_at, updated_at
            FROM claims
            WHERE claims_officer_id = %s
        """
        try:
            results = self.db_handler.execute_query(query, (claims_officer_id,), fetch=True)
            return [
                {
                    "claim_id": str(row[0]),
                    "customer_id": str(row[1]),
                    "policy_id": str(row[2]),
                    "claim_date": row[3].isoformat() if row[3] else None,
                    "status": row[4],
                    "inspection_date": row[5].isoformat() if row[5] else None,
                    "inspection_guide_id": str(row[6]) if row[6] else None,
                    "claims_officer_id": str(row[7]) if row[7] else None,
                    "comments": row[8],
                    "created_at": row[9].isoformat() if row[9] else None,
                    "updated_at": row[10].isoformat() if row[10] else None,
                    "approved_amount": float(row[11]) if row[11] is not None else 0.0
                }
                for row in results
            ] if results else []
        except Exception as e:
            raise Exception(f"Failed to get claims by officer: {e}")

    def get_inspection_appointments(self, claim_id):
        query = """
            SELECT appointment_id, claim_id, inspection_guide_id, appointment_date, status, 
                   inspection_report, created_at, updated_at
            FROM inspection_appointments
            WHERE claim_id = %s
        """
        try:
            results = self.db_handler.execute_query(query, (claim_id,), fetch=True)
            return [
                {
                    "appointment_id": str(row[0]),
                    "claim_id": str(row[1]),
                    "inspection_guide_id": str(row[2]) if row[2] else None,
                    "appointment_date": row[3].isoformat() if row[3] else None,
                    "status": row[4],
                    "inspection_report": row[5],
                    "created_at": row[6].isoformat() if row[6] else None,
                    "updated_at": row[7].isoformat() if row[7] else None
                }
                for row in results
            ] if results else []
        except Exception as e:
            raise Exception(f"Failed to get inspection appointments: {e}")
        
    
  
        
    def get_inspection_appointments_by_id(self, appointment_id):
        query = """
            SELECT appointment_id, claim_id, inspection_guide_id, appointment_date, status, inspection_report, created_at, updated_at
            FROM inspection_appointments
            WHERE appointment_id = %s
        """
        try:
            results = self.db_handler.execute_query(query, (appointment_id,), fetch=True)
            return [{
                "appointment_id": str(row[0]),
                "claim_id": str(row[1]),
                "inspection_guide_id": str(row[2]) if row[2] else None,
                "appointment_date": row[3].isoformat() if row[3] else None,
                "status": row[4],
                "inspection_report": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
                "updated_at": row[7].isoformat() if row[7] else None
            } for row in results]
        except Exception as e:
            raise Exception(f"Failed to fetch appointments: {e}")
        
    def get_claim_by_id(self, claim_id):
        query = """
            SELECT claim_id, policy_id, customer_id, status, created_at, updated_at
            FROM claims
            WHERE claim_id = %s
        """
        try:
            result = self.db_handler.execute_query(query, (claim_id,), fetch=True)
            if result:
                return {
                    "claim_id": str(result[0][0]),
                    "policy_id": str(result[0][1]),
                    "customer_id": str(result[0][2]),
                    "status": result[0][3],
                    "created_at": result[0][4].isoformat(),
                    "updated_at": result[0][5].isoformat()
                }
            return None
        except Exception as e:
            raise Exception(f"Failed to fetch claim: {e}")

    def get_claims_with_inspection_status(self):
        query = """
            SELECT c.claim_id, c.policy_id, c.customer_id, c.status, c.created_at, c.updated_at,
                   ia.appointment_id, ia.status as appointment_status, ia.inspection_report
            FROM claims c
            LEFT JOIN inspection_appointments ia ON c.claim_id = ia.claim_id
            ORDER BY CASE
                WHEN ia.status = 'completed' THEN 1
                WHEN c.status = 'pending_inspection' THEN 2
                ELSE 3
            END, c.created_at DESC
        """
        try:
            results = self.db_handler.execute_query(query, fetch=True)
            return [
                {
                    "claim_id": str(row[0]),
                    "policy_id": str(row[1]),
                    "customer_id": str(row[2]),
                    "status": row[3],
                    "created_at": row[4].isoformat(),
                    "updated_at": row[5].isoformat(),
                    "appointment_id": str(row[6]) if row[6] else None,
                    "appointment_status": row[7],
                    "inspection_report": row[8]
                }
                for row in results
            ]
        except Exception as e:
            raise Exception(f"Failed to fetch claims: {e}")

 
        update_claim_status
  
        
    def get_appointment_by_id(self, claim_id):
        query = """
            SELECT appointment_id, claim_id, inspection_guide_id, appointment_date, status, inspection_report
            FROM inspection_appointments
            WHERE claim_id = %s
        """
        try:
            result = self.db_handler.execute_query(query, (claim_id,), fetch=True)
            if result:
                return {
                    "appointment_id": str(result[0][0]),
                    "claim_id": str(result[0][1]),
                    "inspection_guide_id": str(result[0][2]),
                    "appointment_date": result[0][3].isoformat() if result[0][3] else None,
                    "status": result[0][4],
                    "inspection_report": result[0][5] or {}
                }
            return None
        except Exception as e:
            raise Exception(f"Failed to fetch appointment: {e}")

    def update_inspection_report(self, appointment_id, inspection_report):
        query = """
            UPDATE inspection_appointments
            SET inspection_report = %s, updated_at = CURRENT_TIMESTAMP
            WHERE appointment_id = %s
        """
        try:
            # Serialize inspection_report to JSON
            inspection_report_json = json.dumps(inspection_report)
            self.db_handler.execute_query(query, (inspection_report_json, appointment_id))
        except Exception as e:
            raise Exception(f"Failed to update inspection report: {e}")

    def update_appointment_status(self, appointment_id, status):
        query = """
            UPDATE inspection_appointments
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE appointment_id = %s
        """
        try:
            self.db_handler.execute_query(query, (status, appointment_id))
        except Exception as e:
            raise Exception(f"Failed to update appointment status: {e}")
    def  update_claim_status(self, claim_id,status,approved_amount,comments):
        query = """

            UPDATE claims
            SET status = %s,approved_amount = %s, comments = %s, updated_at = CURRENT_TIMESTAMP
            WHERE claim_id = %s"""
        try: self.db_handler.execute_query(query, (status, claim_id,approved_amount,comments))
        except Exception as e:
            raise Exception(f"Failed to update claim status: {e}")
        
    def get_documents_by_claim_id(self, claim_id):
        query = """
            SELECT document_id, claim_id, document_url, document_type, uploaded_at
            FROM claim_documents
            WHERE claim_id = %s
            ORDER BY uploaded_at DESC
        """
        try:
            results = self.db_handler.execute_query(query, (claim_id,), fetch=True)
            return [
                {
                    "document_id": str(row[0]),
                    "claim_id": str(row[1]),
                    "document_url": row[2],
                    "document_type": row[3],
                    "uploaded_at": row[4].isoformat()
                }
                for row in results
            ]
        except Exception as e:
            raise Exception(f"Failed to fetch documents: {e}")
        
    
   