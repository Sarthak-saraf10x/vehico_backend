import psycopg2
from commons.db_handler import DatabaseHandler
from datetime import datetime
import json

class ClaimDocumentModel:
    def __init__(self, db_config):
        self.db_handler = DatabaseHandler(db_config)

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