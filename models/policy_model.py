import psycopg2
from commons.db_handler import DatabaseHandler
from datetime import datetime

class PolicyModel:
    def __init__(self, db_config):
        self.db_handler = DatabaseHandler(**db_config)

    def create_policy_type(self, name, description, image=None):
        query = """
            INSERT INTO policy_types (name, description, image)
            VALUES (%s, %s, %s)
            RETURNING policy_type_id, name, description, image, created_at, updated_at
        """
        try:
            result = self.db_handler.execute_query(query, (name, description, image), fetch=True)
            return {
                "policy_type_id": str(result[0][0]),
                "name": result[0][1],
                "description": result[0][2],
                "image": result[0][3],
                "created_at": result[0][4].isoformat() if result[0][4] else None,
                "updated_at": result[0][5].isoformat() if result[0][5] else None
            } if result else None
        except Exception as e:
            raise Exception(f"Failed to create policy type: {e}")

    def get_policy_type_by_id(self, policy_type_id):
        query = """
            SELECT policy_type_id, name, description, image, created_at, updated_at
            FROM policy_types
            WHERE policy_type_id = %s
        """
        try:
            result = self.db_handler.execute_query(query, (policy_type_id,), fetch=True)
            return {
                "policy_type_id": str(result[0][0]),
                "name": result[0][1],
                "description": result[0][2],
                "image": result[0][3],
                "created_at": result[0][4].isoformat() if result[0][4] else None,
                "updated_at": result[0][5].isoformat() if result[0][5] else None
            } if result else None
        except Exception as e:
            raise Exception(f"Failed to get policy type: {e}")

    def get_all_policy_types(self):
        query = """
            SELECT policy_type_id, name, description, image, created_at, updated_at
            FROM policy_types
        """
        try:
            result = self.db_handler.execute_query(query, fetch=True)
            return [
                {
                    "policy_type_id": str(row[0]),
                    "name": row[1],
                    "description": row[2] or "",
                    "image": row[3],
                    "created_at": row[4].isoformat() if row[4] else "",
                    "updated_at": row[5].isoformat() if row[5] else ""
                }
                for row in result
            ] if result else []
        except Exception as e:
            raise Exception(f"Failed to get all policy types: {e}")

    def update_policy_type(self, policy_type_id, name=None, description=None, image=None):
        updates = []
        params = []
        if name:
            updates.append("name = %s")
            params.append(name)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if image is not None:
            updates.append("image = %s")
            params.append(image)
        
        if not updates:
            raise Exception("No fields to update")
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(policy_type_id)
        query = f"""
            UPDATE policy_types
            SET {', '.join(updates)}
            WHERE policy_type_id = %s
            RETURNING policy_type_id, name, description, image, created_at, updated_at
        """
        try:
            result = self.db_handler.execute_query(query, tuple(params), fetch=True)
            return {
                "policy_type_id": str(result[0][0]),
                "name": result[0][1],
                "description": result[0][2],
                "image": result[0][3],
                "created_at": result[0][4].isoformat() if result[0][4] else None,
                "updated_at": result[0][5].isoformat() if result[0][5] else None
            } if result else None
        except Exception as e:
            raise Exception(f"Failed to update policy type: {e}")

    def delete_policy_type(self, policy_type_id):
        check_query = """
            SELECT COUNT(*) FROM policies WHERE policy_type_id = %s
        """
        try:
            count = self.db_handler.execute_query(check_query, (policy_type_id,), fetch=True)[0][0]
            if count > 0:
                raise Exception("Cannot delete policy type with associated policies")
            
            query = "DELETE FROM policy_types WHERE policy_type_id = %s"
            self.db_handler.execute_query(query, (policy_type_id,))
            return True
        except Exception as e:
            raise Exception(f"Failed to delete policy type: {e}")

    def create_policy(self, policy_name, policy_number, policy_type_id, price, time_period, start_date, end_date, coverage_details, is_claimable, required_documents_count, documents_list, requires_inspection, inspection_checklist, created_by):
        query = """
            INSERT INTO policies (
                policy_name, policy_number, policy_type_id, price, time_period, start_date, end_date, 
                coverage_details, is_claimable, required_documents_count, documents_list, 
                requires_inspection, inspection_checklist, created_by, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING policy_id, policy_name, policy_number, policy_type_id, price, time_period, 
                      start_date, end_date, coverage_details, is_claimable, required_documents_count, 
                      documents_list, requires_inspection, inspection_checklist, created_by, created_at, updated_at
        """
        try:
            result = self.db_handler.execute_query(query, (
                policy_name, policy_number, policy_type_id, price, time_period, start_date, end_date, 
                coverage_details, is_claimable, required_documents_count, documents_list, 
                requires_inspection, inspection_checklist, created_by
            ), fetch=True)
            return {
                "policy_id": str(result[0][0]),
                "policy_name": result[0][1],
                "policy_number": result[0][2],
                "policy_type_id": str(result[0][3]),
                "price": float(result[0][4]),
                "time_period": result[0][5],
                "start_date": result[0][6].isoformat() if result[0][6] else None,
                "end_date": result[0][7].isoformat() if result[0][7] else None,
                "coverage_details": result[0][8],
                "is_claimable": result[0][9],
                "required_documents_count": result[0][10],
                "documents_list": result[0][11],
                "requires_inspection": result[0][12],
                "inspection_checklist": result[0][13],
                "created_by": str(result[0][14]),
                "created_at": result[0][15].isoformat() if result[0][15] else None,
                "updated_at": result[0][16].isoformat() if result[0][16] else None
            } if result else None
        except Exception as e:
            raise Exception(f"Failed to create policy: {e}")

    def get_policy_by_id(self, policy_id):
        query = """
            SELECT policy_id, policy_name, policy_number, policy_type_id, price, time_period, 
                   start_date, end_date, coverage_details, is_claimable, required_documents_count, 
                   documents_list, requires_inspection, inspection_checklist, created_by, created_at, updated_at
            FROM policies
            WHERE policy_id = %s
        """
        try:
            result = self.db_handler.execute_query(query, (policy_id,), fetch=True)
            return {
                "policy_id": str(result[0][0]),
                "policy_name": result[0][1],
                "policy_number": result[0][2],
                "policy_type_id": str(result[0][3]),
                "price": float(result[0][4]),
                "time_period": result[0][5],
                "start_date": result[0][6].isoformat() if result[0][6] else None,
                "end_date": result[0][7].isoformat() if result[0][7] else None,
                "coverage_details": result[0][8],
                "is_claimable": result[0][9],
                "required_documents_count": result[0][10],
                "documents_list": result[0][11],
                "requires_inspection": result[0][12],
                "inspection_checklist": result[0][13],
                "created_by": str(result[0][14]),
                "created_at": result[0][15].isoformat() if result[0][15] else None,
                "updated_at": result[0][16].isoformat() if result[0][16] else None
            } if result else None
        except Exception as e:
            raise Exception(f"Failed to get policy: {e}")

    def get_all_policies(self):
        query = """
            SELECT policy_id, policy_name, policy_number, policy_type_id, price, time_period, 
                   start_date, end_date, coverage_details, is_claimable, required_documents_count, 
                   documents_list, requires_inspection, inspection_checklist, created_by, created_at, updated_at
            FROM policies
        """
        try:
            results = self.db_handler.execute_query(query, fetch=True)
            return [
                {
                    "policy_id": str(row[0]),
                    "policy_name": row[1],
                    "policy_number": row[2],
                    "policy_type_id": str(row[3]),
                    "price": float(row[4]),
                    "time_period": row[5],
                    "start_date": row[6].isoformat() if row[6] else None,
                    "end_date": row[7].isoformat() if row[7] else None,
                    "coverage_details": row[8],
                    "is_claimable": row[9],
                    "required_documents_count": row[10],
                    "documents_list": row[11],
                    "requires_inspection": row[12],
                    "inspection_checklist": row[13],
                    "created_by": str(row[14]),
                    "created_at": row[15].isoformat() if row[15] else None,
                    "updated_at": row[16].isoformat() if row[16] else None
                }
                for row in results
            ] if results else []
        except Exception as e:
            raise Exception(f"Failed to get policies: {e}")

    def get_policies_by_customer(self, customer_id):
        query = """
            SELECT p.policy_id, p.policy_name, p.policy_number, p.policy_type_id, p.price, p.time_period, 
                   p.start_date, p.end_date, p.coverage_details, p.is_claimable, p.required_documents_count, 
                   p.documents_list, p.requires_inspection, p.inspection_checklist, p.created_by, p.created_at, p.updated_at
            FROM policies p
            JOIN customer_policies cp ON p.policy_id = cp.policy_id
            WHERE cp.customer_id = %s AND cp.status = 'active'
        """
        try:
            results = self.db_handler.execute_query(query, (customer_id,), fetch=True)
            return [
                {
                    "policy_id": str(row[0]),
                    "policy_name": row[1],
                    "policy_number": row[2],
                    "policy_type_id": str(row[3]),
                    "price": float(row[4]),
                    "time_period": row[5],
                    "start_date": row[6].isoformat() if row[6] else None,
                    "end_date": row[7].isoformat() if row[7] else None,
                    "coverage_details": row[8],
                    "is_claimable": row[9],
                    "required_documents_count": row[10],
                    "documents_list": row[11],
                    "requires_inspection": row[12],
                    "inspection_checklist": row[13],
                    "created_by": str(row[14]),
                    "created_at": row[15].isoformat() if row[15] else None,
                    "updated_at": row[16].isoformat() if row[16] else None
                }
                for row in results
            ] if results else []
        except Exception as e:
            raise Exception(f"Failed to get policies by customer: {e}")

    def get_policies_by_created_by(self, created_by):
        query = """
            SELECT policy_id, policy_name, policy_number, policy_type_id, price, time_period, 
                   start_date, end_date, coverage_details, is_claimable, required_documents_count, 
                   documents_list, requires_inspection, inspection_checklist, created_by, created_at, updated_at
            FROM policies
            WHERE created_by = %s
        """
        try:
            results = self.db_handler.execute_query(query, (created_by,), fetch=True)
            return [
                {
                    "policy_id": str(row[0]),
                    "policy_name": row[1],
                    "policy_number": row[2],
                    "policy_type_id": str(row[3]),
                    "price": float(row[4]),
                    "time_period": row[5],
                    "start_date": row[6].isoformat() if row[6] else None,
                    "end_date": row[7].isoformat() if row[7] else None,
                    "coverage_details": row[8],
                    "is_claimable": row[9],
                    "required_documents_count": row[10],
                    "documents_list": row[11],
                    "requires_inspection": row[12],
                    "inspection_checklist": row[13],
                    "created_by": str(row[14]),
                    "created_at": row[15].isoformat() if row[15] else None,
                    "updated_at": row[16].isoformat() if row[16] else None
                }
                for row in results
            ] if results else []
        except Exception as e:
            raise Exception(f"Failed to get policies by created_by: {e}")

    def purchase_policy(self, policy_id, customer_id):
        policy_query = """
            SELECT policy_id FROM policies WHERE policy_id = %s
        """
        try:
            policy = self.db_handler.execute_query(policy_query, (policy_id,), fetch=True)
            if not policy:
                return None

            check_query = """
                SELECT customer_policy_id FROM customer_policies 
                WHERE customer_id = %s AND policy_id = %s AND status = 'active'
            """
            existing_purchase = self.db_handler.execute_query(check_query, (customer_id, policy_id), fetch=True)
            if existing_purchase:
                raise Exception("Customer has already purchased this policy")

            insert_query = """
                INSERT INTO customer_policies (customer_id, policy_id, purchase_date, status)
                VALUES (%s, %s, CURRENT_TIMESTAMP, 'active')
                RETURNING customer_policy_id, customer_id, policy_id, purchase_date, status
            """
            result = self.db_handler.execute_query(insert_query, (customer_id, policy_id), fetch=True)
            
            policy_details_query = """
                SELECT policy_id, policy_name, policy_number, policy_type_id, price, time_period, 
                       start_date, end_date, coverage_details, is_claimable, required_documents_count, 
                       documents_list, requires_inspection, inspection_checklist, created_by, created_at, updated_at
                FROM policies
                WHERE policy_id = %s
            """
            policy_result = self.db_handler.execute_query(policy_details_query, (policy_id,), fetch=True)
            
            return {
                "policy_id": str(policy_result[0][0]),
                "policy_name": policy_result[0][1],
                "policy_number": policy_result[0][2],
                "policy_type_id": str(policy_result[0][3]),
                "price": float(policy_result[0][4]),
                "time_period": policy_result[0][5],
                "start_date": policy_result[0][6].isoformat() if policy_result[0][6] else None,
                "end_date": policy_result[0][7].isoformat() if policy_result[0][7] else None,
                "coverage_details": policy_result[0][8],
                "is_claimable": policy_result[0][9],
                "required_documents_count": policy_result[0][10],
                "documents_list": policy_result[0][11],
                "requires_inspection": policy_result[0][12],
                "inspection_checklist": policy_result[0][13],
                "created_by": str(policy_result[0][14]),
                "created_at": policy_result[0][15].isoformat() if policy_result[0][15] else None,
                "updated_at": policy_result[0][16].isoformat() if policy_result[0][16] else None
            } if policy_result else None
        except Exception as e:
            raise Exception(f"Failed to purchase policy: {e}")

    def update_policy(self, policy_id, policy_name=None, policy_number=None, price=None, time_period=None, start_date=None, end_date=None, coverage_details=None, is_claimable=None, required_documents_count=None, documents_list=None, requires_inspection=None, inspection_checklist=None):
        updates = []
        params = []
        if policy_name:
            updates.append("policy_name = %s")
            params.append(policy_name)
        if policy_number:
            updates.append("policy_number = %s")
            params.append(policy_number)
        if price is not None:
            updates.append("price = %s")
            params.append(price)
        if time_period:
            updates.append("time_period = %s")
            params.append(time_period)
        if start_date:
            updates.append("start_date = %s")
            params.append(start_date)
        if end_date:
            updates.append("end_date = %s")
            params.append(end_date)
        if coverage_details:
            updates.append("coverage_details = %s")
            params.append(coverage_details)
        if is_claimable is not None:
            updates.append("is_claimable = %s")
            params.append(is_claimable)
        if required_documents_count is not None:
            updates.append("required_documents_count = %s")
            params.append(required_documents_count)
        if documents_list is not None:
            updates.append("documents_list = %s")
            params.append(documents_list)
        if requires_inspection is not None:
            updates.append("requires_inspection = %s")
            params.append(requires_inspection)
        if inspection_checklist is not None:
            updates.append("inspection_checklist = %s")
            params.append(inspection_checklist)
        
        if not updates:
            raise Exception("No fields to update")
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(policy_id)
        query = f"""
            UPDATE policies
            SET {', '.join(updates)}
            WHERE policy_id = %s
            RETURNING policy_id, policy_name, policy_number, policy_type_id, price, time_period, 
                      start_date, end_date, coverage_details, is_claimable, required_documents_count, 
                      documents_list, requires_inspection, inspection_checklist, created_by, created_at, updated_at
        """
        try:
            result = self.db_handler.execute_query(query, tuple(params), fetch=True)
            return {
                "policy_id": str(result[0][0]),
                "policy_name": result[0][1],
                "policy_number": result[0][2],
                "policy_type_id": str(result[0][3]),
                "price": float(result[0][4]),
                "time_period": result[0][5],
                "start_date": result[0][6].isoformat() if result[0][6] else None,
                "end_date": result[0][7].isoformat() if result[0][7] else None,
                "coverage_details": result[0][8],
                "is_claimable": result[0][9],
                "required_documents_count": result[0][10],
                "documents_list": result[0][11],
                "requires_inspection": result[0][12],
                "inspection_checklist": result[0][13],
                "created_by": str(result[0][14]),
                "created_at": result[0][15].isoformat() if result[0][15] else None,
                "updated_at": result[0][16].isoformat() if result[0][16] else None
            } if result else None
        except Exception as e:
            raise Exception(f"Failed to update policy: {e}")

    def delete_policy(self, policy_id):
        check_query = """
            SELECT end_date FROM policies WHERE policy_id = %s
        """
        try:
            result = self.db_handler.execute_query(check_query, (policy_id,), fetch=True)
            if result:
                end_date = result[0][0]
                if end_date and end_date > datetime.now().date():
                    check_purchases = """
                        SELECT COUNT(*) FROM customer_policies WHERE policy_id = %s AND status = 'active'
                    """
                    count = self.db_handler.execute_query(check_purchases, (policy_id,), fetch=True)[0][0]
                    if count > 0:
                        raise Exception("Cannot delete policy with active customer purchases")
            
            query = "DELETE FROM policies WHERE policy_id = %s"
            self.db_handler.execute_query(query, (policy_id,))
            return True
        except Exception as e:
            raise Exception(f"Failed to delete policy: {e}")
        
   
   
    def get_policy_checklist(self, policy_id):
        try:
            policy = self.get_policy_by_id(policy_id)
            if not policy:
                raise ValueError("Policy not found")
            checklist = policy['inspection_checklist'] or []
            # Transform string-based checklist to object format
            if checklist and isinstance(checklist[0], str):
                checklist = [
                    {"id": str(i + 1), "question": item, "type": "text"}
                    for i, item in enumerate(checklist)
                ]
            return checklist
        except Exception as e:
            raise Exception(f"Failed to fetch checklist: {e}")
        
    def get_policies_with_claim_counts(self, user_id):
        query = """
            SELECT p.policy_id, p.inspection_checklist, p.created_at, p.updated_at,
                   COUNT(c.claim_id) as claim_count
            FROM policies p
            LEFT JOIN claims c ON p.policy_id = c.policy_id
            WHERE p.user_id = %s
            GROUP BY p.policy_id, p.inspection_checklist, p.created_at, p.updated_at
            ORDER BY p.created_at DESC
        """
        try:
            results = self.db_handler.execute_query(query, (user_id,), fetch=True)
            return [
                {
                    "policy_id": str(row[0]),
                    "inspection_checklist": row[1],
                    "created_at": row[2].isoformat(),
                    "updated_at": row[3].isoformat(),
                    "claim_count": row[4]
                }
                for row in results
            ]
        except Exception as e:
            raise Exception(f"Failed to fetch policies: {e}")

 