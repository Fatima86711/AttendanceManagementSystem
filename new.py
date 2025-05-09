# from database import get_connection

# try:
#     conn = get_connection()
#     cursor = conn.cursor()
#     query = "SELECT email, password FROM teachers"
#     cursor.execute(query)
#     data = cursor.fetchall()
#     print(f"DEBUG: Data in teachers table: {data}")
#     # print("DEBUG: Data in teachers table: [('ali.khan@university.edu.pk', 'secure123'), ('fatima.ahmed@university.edu.pk', 'mypassword')]")
#     cursor.close()
#     conn.close()
# except Exception as e:
#     print(f"DEBUG: Database error: {e}")

import oracledb

def get_connection():
    try:
        conn = oracledb.connect(user="System", password="Server123", dsn="localhost/orcal")
        return conn
    except oracledb.DatabaseError as e:
        print(f"DEBUG: Database connection error - {e}")
        return None

# Test the connection
conn = get_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT 'Connection Successful' AS status FROM dual")
    result = cursor.fetchone()
    print(f"DEBUG: {result[0]}")  # Output: Connection Successful
    cursor.close()
    conn.close()
else:
    print("DEBUG: Connection failed!")

    