import tkinter as tk
from tkinter import messagebox
from teacher_dashboard import TeacherDashboard  # Import TeacherDashboard class
from student_dashboard import StudentDashboard  # Import StudentDashboard class
from database import get_connection

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

        tk.Button(self, text="Login", font=("Arial", 12), command=self.validate_login).pack(pady=20)
        
    def validate_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Warning", "All fields are required!")
            return
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Debugging
            print(f"DEBUG: Email entered: {email}")
            print(f"DEBUG: Password entered: {password}")
            
            # First check if teacher
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
                return  # exit after successful teacher login

            # Now check if student
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
                StudentDashboard(student_id).mainloop()  # <-- Remove student_name
            else:
                messagebox.showerror("Error", "Invalid email or password!")
            
            cursor.close()
            conn.close()

        except Exception as e:
            print(f"DEBUG: Database error: {e}")
            messagebox.showerror("Error", f"Database Error: {e}")

if __name__ == "__main__":
    app = LoginForm()
    app.mainloop()