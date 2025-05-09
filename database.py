import cx_Oracle

def get_connection():
    try:
        # Replace with your actual connection details
        dsn = cx_Oracle.makedsn("localhost", 1521, service_name="ORCAL")  # Update hostname and port if needed
        conn = cx_Oracle.connect(user="System", password="Server123", dsn=dsn)  # Replace username and password
        return conn
    except cx_Oracle.DatabaseError as e:
        raise Exception(f"Database connection error: {e}")