# commons/db_handler.py
import psycopg2
from psycopg2 import pool
import logging
from dotenv import load_dotenv


class DatabaseHandler:
    def __init__(self, dbname, user, password, host, port, minconn=1, maxconn=10):
        """
        Initialize the database connection pool.
        
        Args:
            dbname (str): Database name
            user (str): Database user
            password (str): Database password
            host (str): Database host
            port (str): Database port
            minconn (int): Minimum connections in pool
            maxconn (int): Maximum connections in pool
        """
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection_pool = None
        self.minconn = minconn
        self.maxconn = maxconn
        self.logger = logging.getLogger(__name__)

        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                self.minconn, self.maxconn,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.logger.info("Database connection pool created successfully")
        except Exception as e:
            self.logger.error(f"Error creating connection pool: {e}")
            raise

    def get_connection(self):
        """Get a connection from the pool."""
        try:
            return self.connection_pool.getconn()
        except Exception as e:
            self.logger.error(f"Error getting connection from pool: {e}")
            raise

    def release_connection(self, conn):
        """Release a connection back to the pool."""
        try:
            self.connection_pool.putconn(conn)
        except Exception as e:
            self.logger.error(f"Error releasing connection: {e}")
            raise

    def close_all_connections(self):
        """Close all connections in the pool."""
        try:
            if self.connection_pool:
                self.connection_pool.closeall()
                self.logger.info("All database connections closed")
        except Exception as e:
            self.logger.error(f"Error closing connections: {e}")
            raise

    def execute_query(self, query, params=None, fetch=False):
        """
        Execute a SQL query.
        
        Args:
            query (str): SQL query to execute
            params (tuple): Parameters for the query (optional)
            fetch (bool): Whether to fetch results (True for SELECT, False for INSERT/UPDATE/DELETE)
        
        Returns:
            list: Query results if fetch=True, None otherwise
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch:
                results = cursor.fetchall()
            else:
                results = None
            conn.commit()
                
            return results
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.release_connection(conn)