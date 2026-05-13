import psycopg2
from commons.db_handler import DatabaseHandler
from datetime import datetime
import json
class InspectionAppointmentModel:
    def __init__(self, db_config):
        self.db_handler = DatabaseHandler(db_config)

    def get_appointment_by_id(self, appointment_id):
        query = """
            SELECT appointment_id, claim_id, inspection_guide_id, appointment_date, status, inspection_report
            FROM inspection_appointments
            WHERE appointment_id = %s
        """
        try:
            result = self.db_handler.execute_query(query, (appointment_id,), fetch=True)
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
            self.db_handler.execute_query(query, (inspection_report, appointment_id))
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