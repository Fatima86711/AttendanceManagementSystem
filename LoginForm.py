import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Import ttk for Combobox and Treeview
import cx_Oracle  # Import the cx_Oracle library
from teacher_dashboard import TeacherDashboard
from student_dashboard import StudentDashboard

# Database connection details (replace with your actual credentials)
DB_CONFIG = {
    'user': 'System',
    'password': 'Server123',
    'dsn': 'localhost/ORCAL'  #  (e.g., 'localhost/orcl')
}

def get_connection():
    """
    Establishes a connection to the Oracle database.
    """
    try:
        connection = cx_Oracle.connect(
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            dsn=DB_CONFIG['dsn']
        )
        return connection
    except cx_Oracle.Error as e:
        messagebox.showerror("Database Connection Error", f"Error connecting to the database: {e}")
        return None  # Important: Return None on error

class CRUDWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("CRUD Operations")
        self.geometry("800x600")
        self.parent = parent
        self.tables = ["students", "teachers", "attendance", "courses", "enrollments", "assignments", "leave_requests"]
        self.table_combobox = ttk.Combobox(self, values=self.tables, font=("Arial", 12))
        self.table_combobox.pack(pady=10)
        self.table_combobox.set(self.tables[0])
        tk.Button(self, text="Perform Operations", font=("Arial", 12), command=self.show_operation_selection).pack(pady=10)
        self.result_label = tk.Label(self, text="", font=("Arial", 12), wraplength=400)
        self.result_label.pack(pady=10)
        self.data_treeview = ttk.Treeview(self, show="headings", selectmode="browse")
        self.data_treeview.pack(pady=10, fill=tk.BOTH, expand=True)
        self.data_treeview.columnconfigure(0, weight=1)

        self.back_button = tk.Button(self, text="Back", font=("Arial", 12), command=self.on_close)
        self.back_button.pack(pady=10)

    def show_operation_selection(self):
        selected_table = self.table_combobox.get()
        operation_window = tk.Toplevel(self)
        operation_window.title(f"Operations for {selected_table}")
        operation_window.geometry("300x200")
        operations = ["Read", "Update", "Delete", "Insert"]
        tk.Label(operation_window, text="Select operation:", font=("Arial", 12)).pack(pady=10)
        operation_combobox = ttk.Combobox(operation_window, values=operations, font=("Arial", 12))
        operation_combobox.pack(pady=10)
        operation_combobox.set(operations[0])
        tk.Button(operation_window, text="Confirm", font=("Arial", 12),
                  command=lambda: self.perform_operation(selected_table, operation_combobox.get(), operation_window)).pack(pady=10)
        operation_window.back_button = tk.Button(operation_window, text="Back", font=("Arial", 12), command=operation_window.destroy)
        operation_window.back_button.pack(pady=10)

    def perform_operation(self, selected_table, selected_operation, operation_window):
        operation_window.destroy()
        self.result_label.config(text=f"Performing {selected_operation} on table: {selected_table}")
        if selected_operation == "Read":
            self.read_data_from_table(selected_table)
        elif selected_operation == "Update":
            self.open_update_dialog(selected_table)
        elif selected_operation == "Delete":
            self.delete_record_from_table(selected_table)
        elif selected_operation == "Insert":
            self.open_insert_dialog(selected_table)

    def read_data_from_table(self, table_name):
        try:
            conn = get_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            self._populate_treeview(columns, data)
            self.result_label.config(text=f"Data from table '{table_name}' displayed.")
            cursor.close()
            conn.close()
        except cx_Oracle.Error as e:
            self.handle_database_error(e, f"Error reading data from table '{table_name}'")

    def _populate_treeview(self, columns, data):
        for item in self.data_treeview.get_children():
            self.data_treeview.delete(item)
        self.data_treeview["columns"] = columns
        for col in columns:
            self.data_treeview.heading(col, text=col)
            self.data_treeview.column(col, width=100, stretch=True)
        for row in data:
            self.data_treeview.insert("", tk.END, values=row)

    def delete_record_from_table(self, table_name):
        """
        Deletes a selected record from the specified table and handles
        foreign key constraints for the 'students' table.

        Args:
            table_name (str): The name of the table from which to delete the record.
        """
        selected_item = self.data_treeview.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return
        record_values = self.data_treeview.item(selected_item)['values']
        if not record_values:
            messagebox.showwarning("Warning", "No record to delete.")
            return

        try:
            conn = get_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            primary_key_column = self.data_treeview["columns"][0]
            primary_key_value = record_values[0]

            if table_name == "students":
                # Identify child tables that have a foreign key referencing students(student_id)
                child_tables = ["enrollments", "attendance"]  # Based on your provided schema

                # Delete related records in child tables
                for child_table in child_tables:
                    delete_child_query = f"DELETE FROM {child_table} WHERE student_id = :1"
                    try:
                        cursor.execute(delete_child_query, (primary_key_value,))
                        print(f"DEBUG: Deleted {cursor.rowcount} records from {child_table} for student_id {primary_key_value}")
                    except cx_Oracle.Error as e:
                        messagebox.showerror("Database Error", f"Error deleting related records from {child_table}: {e}")
                        conn.rollback()
                        cursor.close()
                        conn.close()
                        return

                # Handle assignments table separately as it doesn't directly link to student_id
                delete_assignments_query = "DELETE FROM assignments WHERE teacher_id IN (SELECT teacher_id FROM teachers WHERE department_name = (SELECT department_name FROM students WHERE student_id = :1))"
                try:
                    cursor.execute(delete_assignments_query, (primary_key_value,))
                    print(f"DEBUG: Deleted {cursor.rowcount} records from assignments related to student's department for student_id {primary_key_value}")
                except cx_Oracle.Error as e:
                    messagebox.showerror("Database Error", f"Error deleting related records from assignments: {e}")
                    conn.rollback()
                    cursor.close()
                    conn.close()
                    return

                delete_leave_requests_query = "DELETE FROM leave_requests WHERE student_id = :1"
                try:
                    cursor.execute(delete_leave_requests_query, (primary_key_value,))
                    print(f"DEBUG: Deleted {cursor.rowcount} records from leave_requests for student_id {primary_key_value}")
                except cx_Oracle.Error as e:
                    messagebox.showerror("Database Error", f"Error deleting related records from leave_requests: {e}")
                    conn.rollback()
                    cursor.close()
                    conn.close()
                    return

            # Now delete the record from the selected table
            query = f"DELETE FROM {table_name} WHERE {primary_key_column} = :1"
            cursor.execute(query, (primary_key_value,))
            conn.commit()

            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Record deleted successfully.")
                self.read_data_from_table(table_name)  # Refresh the Treeview
            else:
                messagebox.showerror("Error", "Failed to delete record.")

            cursor.close()
            conn.close()

        except cx_Oracle.Error as e:
            conn.rollback()  # Rollback changes in case of error
            self.handle_database_error(e, f"Error deleting record from table '{table_name}'")
    
    
    
    def open_insert_dialog(self, table_name):
        try:
            conn = get_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute(f"SELECT column_name FROM user_tab_cols WHERE table_name = :1", (table_name.upper(),))
            columns_info = cursor.fetchall()
            columns = [info[0] for info in columns_info]
            insert_dialog = tk.Toplevel(self)
            insert_dialog.title(f"Insert Record into {table_name}")
            entries = {}
            for i, column in enumerate(columns):
                tk.Label(insert_dialog, text=f"{column}:", font=("Arial", 12)).grid(row=i, column=0, padx=5, pady=5, sticky="w")
                entry = tk.Entry(insert_dialog, font=("Arial", 12))
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                entries[column] = entry
            insert_button = tk.Button(insert_dialog, text="Insert", font=("Arial", 12),
                                       command=lambda: self.insert_new_record(table_name, columns, entries, insert_dialog))
            insert_button.grid(row=len(columns), column=0, columnspan=2, pady=10)
            insert_dialog.back_button = tk.Button(insert_dialog, text="Back", font=("Arial", 12), command=insert_dialog.destroy)
            insert_dialog.back_button.grid(row=len(columns)+1, column=0, columnspan=2, pady=10)

            cursor.close()
            conn.close()
        except cx_Oracle.Error as e:
            self.handle_database_error(e, f"Error fetching table information for '{table_name}'")

    def insert_new_record(self, table_name, columns, entries, insert_dialog):
        values = []
        column_names = []
        for col in columns:
            value = entries[col].get().strip()
            values.append(value)
            column_names.append(col)

        placeholders = ", ".join([":{}".format(i + 1) for i in range(len(columns))])
        sql = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"

        try:
            conn = get_connection()
            if conn is None:
                return
            cursor = conn.cursor()

            # Convert DATE_OF_BIRTH string to a format Oracle understands
            date_of_birth_index = -1
            try:
                date_of_birth_index = column_names.index('DATE_OF_BIRTH')
                # No need to embed TO_DATE in the SQL here. Let cx_Oracle handle the binding.
                pass
            except ValueError:
                pass # DATE_OF_BIRTH column might not exist

            if date_of_birth_index != -1 and values[date_of_birth_index]:
                try:
                    # You might need to adjust the format string to match user input exactly
                    import datetime
                    values[date_of_birth_index] = datetime.datetime.strptime(values[date_of_birth_index], '%Y-%m-%d').date()
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD for Date of Birth.")
                    cursor.close()
                    conn.close()
                    return

            cursor.execute(sql, values)
            conn.commit()
            messagebox.showinfo("Success", "Record inserted successfully.")
            self.read_data_from_table(table_name)
            insert_dialog.destroy()
            cursor.close()
            conn.close()
        except cx_Oracle.Error as e:
            self.handle_database_error(e, f"Error inserting record into table '{table_name}'")
    
    
    def open_update_dialog(self, table_name):
        if table_name != "students":
            messagebox.showerror("Error", f"Update operation is only supported for the 'students' table.")
            return

        selected_item = self.data_treeview.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a student record to update.")
            return

        student_data = self.data_treeview.item(selected_item)['values']
        if not student_data:
            messagebox.showwarning("Warning", "No data to update for the selected record.")
            return

        self.student_id = student_data[0]  # Assuming student_id is the first column
        columns = self.data_treeview["columns"]  # Get column names

        self.update_dialog = tk.Toplevel(self)
        self.update_dialog.title("Update Student Record")
        tk.Label(self.update_dialog, text="Select column to update:", font=("Arial", 12)).pack(pady=10)
        self.column_combobox = ttk.Combobox(self.update_dialog, values=columns[1:], font=("Arial", 12))  # Exclude student_id
        self.column_combobox.pack(pady=10)
        self.column_combobox.set(columns[1])

        tk.Label(self.update_dialog, text="Enter new value:", font=("Arial", 12)).pack(pady=5)
        self.value_entry = tk.Entry(self.update_dialog, font=("Arial", 12))
        self.value_entry.pack(pady=5)

        self.update_button = tk.Button(self.update_dialog, text="Update", font=("Arial", 12), command=self.update_record)
        self.update_button.pack(pady=10)

        self.update_dialog.back_button = tk.Button(self.update_dialog, text="Back", font=("Arial", 12), command=self.update_dialog.destroy)
        self.update_dialog.back_button.pack(pady=10)

    def update_record(self):
        selected_column = self.column_combobox.get()
        new_value = self.value_entry.get().strip()

        if not new_value:
            messagebox.showwarning("Warning", "Please enter a value to update.")
            return

        try:
            conn = get_connection()
            if conn is None:
                return
            cursor = conn.cursor()

            # Fetch column data type and constraints
            cursor.execute(
                """
                SELECT data_type, data_length
                FROM user_tab_columns
                WHERE table_name = 'STUDENTS' AND column_name = :column_name
                """,
                {'column_name': selected_column.upper()}  # important to use upper()
            )
            column_info = cursor.fetchone()

            if not column_info:
                messagebox.showerror("Error", f"Column '{selected_column}' not found in 'students' table.")
                cursor.close()
                conn.close()
                return

            data_type, data_length = column_info
            print(f"DEBUG: Column: {selected_column}, Type: {data_type}, Length: {data_length}")

            # Basic data type and length validation
            if data_type in ('VARCHAR2', 'CHAR') and len(new_value) > data_length:
                messagebox.showwarning("Warning", f"Value exceeds maximum length ({data_length}) for column '{selected_column}'.")
                cursor.close()
                conn.close()
                return
            elif data_type == 'NUMBER':
                try:
                    float(new_value)  # Check if it's a valid number
                except ValueError:
                    messagebox.showwarning("Warning", f"Invalid data type for column '{selected_column}'.  Please enter a number.")
                    cursor.close()
                    conn.close()
                    return

            # Update the record
            query = f"UPDATE students SET {selected_column} = :new_value WHERE student_id = :student_id"
            cursor.execute(query, {'new_value': new_value, 'student_id': self.student_id})
            conn.commit()

            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Student record updated successfully.")
                self.read_data_from_table('students')  # Refresh the Treeview
                self.update_dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to update student record.")

            cursor.close()
            conn.close()
        except cx_Oracle.Error as e:
            self.handle_database_error(e, "Error updating student record")

    def handle_database_error(self, e, message):
        """
        Handles database errors consistently.
        """
        print(f"DEBUG: {message}: {e}")
        messagebox.showerror("Database Error", f"{message}: {e}")
        self.result_label.config(text=f"{message}: {e}")

    def on_close(self):
        self.destroy()
        self.parent.deiconify()

class LoginForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login Form")
        self.geometry("400x350")
        tk.Label(self, text="Login", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self, text="Email:", font=("Arial", 12)).pack(pady=5)
        self.email_entry = tk.Entry(self, font=("Arial", 12))
        self.email_entry.pack(pady=5)
        tk.Label(self, text="Password:", font=("Arial", 12)).pack(pady=5)
        self.password_entry = tk.Entry(self, font=("Arial", 12), show="*")
        self.password_entry.pack(pady=5)
        self.login_button = tk.Button(self, text="Login", font=("Arial", 12), command=self.validate_login)
        self.login_button.pack(pady=10)
        self.crud_button = tk.Button(self, text="Open CRUD Operations", font=("Arial", 12), command=self.open_crud_window)
        self.crud_button.pack(pady=10)
        self.crud_window = None

    def open_crud_window(self):
        self.withdraw()
        self.crud_window = CRUDWindow(self)
        self.wait_window(self.crud_window)
        self.deiconify()

    def validate_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        if not email or not password:
            messagebox.showwarning("Warning", "All fields are required!")
            return
        try:
            conn = get_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            print(f"DEBUG: Email entered: {email}")
            print(f"DEBUG: Password entered: {password}")
            teacher_query = "SELECT teacher_id FROM teachers WHERE LOWER(email) = LOWER(:email) AND password = :password"
            cursor.execute(teacher_query, {'email': email, 'password': password})
            teacher_result = cursor.fetchone()
            print(f"DEBUG: Teacher query result: {teacher_result}")
            if teacher_result:
                teacher_id = teacher_result[0]
                messagebox.showinfo("Success", "Teacher login successful!")
                self.destroy()
                TeacherDashboard(teacher_id).mainloop()
                cursor.close()
                conn.close()
                return
            student_query = """
                SELECT student_id, first_name || ' ' || last_name AS full_name
                FROM students
                WHERE LOWER(email) = LOWER(:email) AND password = :password
                """
            cursor.execute(student_query, {'email': email, 'password': password})
            student_result = cursor.fetchone()
            print(f"DEBUG: Student query result: {student_result}")
            if student_result:
                student_id = student_result[0]
                student_name = student_result[1]
                messagebox.showinfo("Success", "Student login successful!")
                self.destroy()
                StudentDashboard(student_id).mainloop()
            else:
                messagebox.showerror("Error", "Invalid email or password!")
            cursor.close()
            conn.close()
        except cx_Oracle.Error as e:
            messagebox.showerror("Database Error", f"Error during login: {e}")

if __name__ == "__main__":
    app = LoginForm()
    app.mainloop()
