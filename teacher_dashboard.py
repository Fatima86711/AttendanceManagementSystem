import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import datetime
import calendar
from database import get_connection

class TeacherDashboard(tk.Tk):
    def __init__(self, teacher_id):
        super().__init__()
        self.teacher_id = teacher_id
        self.title("Teacher Dashboard")
        self.geometry("600x400")

        tk.Label(self, text="Welcome to Attendance System", font=("Arial", 18, "bold")).pack(pady=10)

        self.course_listbox = tk.Listbox(self, font=("Arial", 12), width=50, height=10)
        self.course_listbox.pack(pady=10)

        self.load_courses()

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Mark Attendance", font=("Arial", 12, "bold"), command=self.open_attendance_window).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="View Attendance Records", font=("Arial", 12), command=self.view_attendance_records).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Add Student to Course", font=("Arial", 12), command=self.add_student_to_course).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Leave Requests", font=("Arial", 12, "bold"), command=self.view_leave_requests).grid(row=1, column=1, pady=10)

        tk.Button(self, text="Logout", font=("Arial", 10), command=self.logout).pack(pady=10)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()

    def load_courses(self):
        try:
            conn = get_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            query = """
                SELECT course_id, course_name
                FROM teacher_courses_view
                WHERE teacher_id = :teacher_id
            """
            cursor.execute(query, {'teacher_id': self.teacher_id})
            self.courses = cursor.fetchall()
            self.course_listbox.delete(0, tk.END)
            for course in self.courses:
                self.course_listbox.insert(tk.END, f"{course[0]} - {course[1]}")
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Database Error: {e}")

    def get_selected_course(self):
        selected_index = self.course_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select a course!")
            return None
        return self.courses[selected_index[0]]

    def open_attendance_window(self):
        selected_index = self.course_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select a course!")
            return
        selected_course = self.courses[selected_index[0]]
        if not selected_course:
            messagebox.showerror("Error", "Invalid course selection.")
            return
        course_id, course_name = selected_course
        AttendanceWindow(self, self.teacher_id, course_id, course_name)

    def view_attendance_records(self):
        selected_course = self.get_selected_course()
        if selected_course:
            AttendanceRecordsWindow(self, selected_course[0], selected_course[1])

    def add_student_to_course(self):
        selected_course = self.get_selected_course()
        if selected_course:
            AddStudentWindow(self, selected_course[0], selected_course[1])

    def view_leave_requests(self):
        LeaveRequestsWindow(self, self.teacher_id)


class LeaveRequestsWindow(tk.Toplevel):
    def __init__(self, parent, teacher_id):
        super().__init__(parent)
        self.title("Leave Requests")
        self.geometry("600x400")
        self.teacher_id = teacher_id
        self.parent = parent
        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w", padx=10)

        self.leave_tree = ttk.Treeview(self, columns=("Student ID", "Course", "Date", "Reason", "Status"), show='headings')

        for col in ("Student ID", "Course", "Date", "Reason", "Status"):
            self.leave_tree.heading(col, text=col)
            self.leave_tree.column(col, width=100, anchor="center")

        self.leave_tree.pack(pady=10, fill="both", expand=True)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Approve Leave", command=self.approve_leave).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Disapprove Leave", command=self.disapprove_leave).grid(row=0, column=1, padx=5)


        self.load_leave_requests()

    def load_leave_requests(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
    SELECT
        student_id,
        course_name,
        leave_date,
        reason,
        status
    FROM pending_leave_requests_view
    """)

            self.leave_tree.delete(*self.leave_tree.get_children())

            for row in cursor.fetchall():
                self.leave_tree.insert('', tk.END, values=row)

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load leave requests: {e}")



    def go_back(self):
        self.destroy()
        self.parent.deiconify()

    def approve_leave(self): # Added approve_leave method
        selected_item = self.leave_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a leave request to approve.")
            return

        selected_values = self.leave_tree.item(selected_item)['values']
        student_id, course_name, leave_date, reason, status = selected_values  # Unpack all values

        if not messagebox.askyesno("Confirm", "Are you sure you want to approve this leave?"):
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE leave_requests
                SET status = 'Approved'
                WHERE student_id = :student_id AND leave_date = TO_DATE(:leave_date, 'YYYY-MM-DD')
                AND course_id = (SELECT course_id FROM courses WHERE course_name = :course_name)
            """, {
                'student_id': student_id,
                'leave_date': leave_date,
                'course_name': course_name
            })

            cursor.execute("""
                INSERT INTO attendance (ATTENDANCE_ID, STUDENT_ID, COURSE_ID, DATE_ATTENDED, DAY_ATTENDED, STATUS)
                VALUES (attendance_seq.NEXTVAL, :student_id,
                        (SELECT course_id FROM courses WHERE course_name = :course_name),
                        TO_DATE(:leave_date, 'YYYY-MM-DD'),
                        :day_attended, 'Leave')
            """, {
                'student_id': student_id,
                'leave_date': leave_date,
                'course_name': course_name,
                'day_attended': calendar.day_name[datetime.datetime.strptime(leave_date, '%Y-%m-%d').weekday()]
            })

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Leave approved and updated in attendance.")
            self.leave_tree.delete(selected_item)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve leave: {e}")

    def disapprove_leave(self):
        selected_item = self.leave_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a leave request to disapprove.")
            return

        selected_values = self.leave_tree.item(selected_item)['values']
        student_id, course_name, leave_date, reason, status = selected_values

        if not messagebox.askyesno("Confirm", "Are you sure you want to disapprove this leave?"):
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE leave_requests
                SET status = 'Rejected'
                WHERE student_id = :student_id AND leave_date = TO_DATE(:leave_date, 'YYYY-MM-DD')
                AND course_id = (SELECT course_id FROM courses WHERE course_name = :course_name)
            """, {
                'student_id': student_id,
                'leave_date': leave_date,
                'course_name': course_name,
            })

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Leave disapproved.")
            self.leave_tree.delete(selected_item)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to disapprove leave: {e}")



class AttendanceWindow(tk.Toplevel):
    def __init__(self, parent, teacher_id, course_id, course_name):
        super().__init__(parent)
        self.title(f"Mark Attendance - {course_name}")
        self.geometry("750x600")
        self.teacher_id = teacher_id
        self.course_id = course_id
        self.course_name = course_name
        self.parent = parent
        tk.Label(self, text=f"Mark Attendance for {course_name}", font=("Arial", 16, "bold")).pack(pady=10)
        back_button = tk.Button(self, text="\u2190 Back", command = self.go_back, font=("Arial", 12))
        back_button.pack(pady = 5, anchor = "w", padx=10)
        tk.Label(self, text="Select Attendance Date:", font=("Arial", 12)).pack()
        self.date_picker = DateEntry(self, width=12, font=("Arial", 12))
        self.date_picker.pack(pady=5)

        frame = tk.Frame(self)
        frame.pack(pady=10, fill="both", expand=True)

        tk.Label(frame, text="Student ID - Name", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=5)
        tk.Label(frame, text="Status", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10, pady=5, columnspan=3)

        self.attendance_vars = {}

        self.load_students(frame)

        save_btn = tk.Button(self, text="Save Attendance", font=("Arial", 12, "bold"), command=self.save_attendance)
        save_btn.pack(pady=10)

    def load_students(self, frame):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                SELECT s.student_id, (s.first_name || ' ' || s.last_name) AS student_name
                FROM course_students_view s
                WHERE s.course_id = :course_id
            """
            cursor.execute(query, {'course_id': self.course_id})

            for idx, (student_id, student_name) in enumerate(cursor.fetchall(), start=1):
                tk.Label(frame, text=f"{student_id} - {student_name}", font=("Arial", 12)).grid(row=idx, column=0, sticky="w", padx=10, pady=5)

                var = tk.StringVar(value=self.get_leave_status(student_id, self.date_picker.get_date()))

                if var.get() == "Leave":
                    tk.Label(frame, text="Leave (Approved)", font=("Arial", 12, "bold")).grid(row=idx, column=1, padx=5, columnspan=3)
                else:
                    tk.Radiobutton(frame, text="Present", variable=var, value="Present").grid(row=idx, column=1, padx=5)
                    tk.Radiobutton(frame, text="Absent", variable=var, value="Absent").grid(row=idx, column=2, padx=5)
                    tk.Radiobutton(frame, text="Leave", variable=var, value="Leave").grid(row=idx, column=3, padx=5)

                self.attendance_vars[student_id] = var

            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {e}")

    def get_leave_status(self, student_id, selected_date):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT STATUS FROM leave_requests
                WHERE STUDENT_ID = :student_id
                AND LEAVE_DATE = TO_DATE(:date_attended, 'YYYY-MM-DD')
                AND STATUS = 'Approved'
            """, {
                'student_id': student_id,
                'date_attended': selected_date.strftime('%Y-%m-%d')
            })

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            return result[0] if result else "Present"

        except Exception as e:
            messagebox.showerror("Error", f"Failed to check leave status: {e}")
            return "Present"

    def save_attendance(self):
        selected_date = self.date_picker.get_date()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            for student_id, var in self.attendance_vars.items():
                status = var.get()

                cursor.execute("""
                    SELECT STATUS FROM leave_requests
                    WHERE STUDENT_ID = :student_id AND LEAVE_DATE = TO_DATE(:date_attended, 'YYYY-MM-DD') AND STATUS = 'Approved'
                """, {
                    'student_id': student_id,
                    'date_attended': selected_date.strftime('%Y-%m-%d')
                })

                leave_result = cursor.fetchone()
                if leave_result:
                    status = 'Leave'

                cursor.execute("""
                    INSERT INTO ATTENDANCE (ATTENDANCE_ID, STUDENT_ID, COURSE_ID, DATE_ATTENDED, DAY_ATTENDED, STATUS)
                    VALUES (attendance_seq.NEXTVAL, :student_id, :course_id,
                            TO_DATE(:date_attended, 'YYYY-MM-DD'),
                            :day_attended, :status)
                """, {
                    'student_id': student_id,
                    'course_id': self.course_id,
                    'date_attended': selected_date.strftime('%Y-%m-%d'),
                    'day_attended': calendar.day_name[selected_date.weekday()],
                    'status': status
                })

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Attendance saved.")
            self.destroy()
            self.master.deiconify()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save attendance: {e}")

    def go_back(self):
        self.destroy()
        self.parent.deiconify()

class AttendanceRecordsWindow(tk.Toplevel):
    def __init__(self, parent, course_id, course_name):
        super().__init__(parent)
        self.title(f"Attendance Records -{course_name}")
        self.geometry("700x500")
        self.parent = parent

        tk.Label(self, text=f"Attendance Records for {course_name}", font=("Arial", 14, "bold")).pack(pady=10)
        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w", padx=10) # Align to the left

        tk.Label(self, text="Select Date:").pack()
        self.date_picker = DateEntry(self, width=12, font=("Arial", 12))
        self.date_picker.pack(pady=5)

        tk.Button(self, text="Load Records", command=lambda: self.load_records(course_id)).pack(pady=5)

        self.tree = ttk.Treeview(self, columns=("Student ID", "Date", "Status"), show='headings')
        for col in ("Student ID", "Date", "Status"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.load_records(course_id)

    def load_records(self, course_id):
        selected_date = self.date_picker.get_date().strftime('%Y-%m-%d')
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
    SELECT STUDENT_ID, DATE_ATTENDED, STATUS
    FROM ATTENDANCE
    WHERE COURSE_ID = :course_id
    AND TRUNC(DATE_ATTENDED) = TO_DATE(:selected_date, 'YYYY-MM-DD')
    ORDER BY DATE_ATTENDED DESC
""", {'course_id': course_id, 'selected_date': selected_date})

            self.tree.delete(*self.tree.get_children())

            for row in cursor.fetchall():
                formatted_date = row[1].strftime('%Y-%m-%d')
                self.tree.insert('', tk.END, values=(row[0], formatted_date, row[2]))

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load attendance records: {e}")
    def go_back(self):
        self.destroy()
        self.parent.deiconify()
# --- AddStudentWindow Definition ---
class AddStudentWindow(tk.Toplevel):
    def __init__(self, parent, course_id, course_name):
        super().__init__(parent)
        self.title(f"Add Student to {course_name}")
        self.geometry("400x200")
        self.course_id = course_id
        self.parent = parent # Store the parent window

        # Back Button
        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w", padx=10)

        tk.Label(self, text="Student ID:").pack(pady=5)
        self.student_id_entry = tk.Entry(self)
        self.student_id_entry.pack(pady=5)

        tk.Button(self, text="Add Student", command=self.add_student).pack(pady=10)

    def add_student(self):
        student_id = self.student_id_entry.get().strip()
        if not student_id:
            messagebox.showwarning("Input Error", "Please enter a student ID.")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO enrollments (student_id, course_id)
                VALUES (:student_id, :course_id)
            """
            cursor.execute(query, {'student_id': student_id, 'course_id': self.course_id})
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", f"Student {student_id} added to course.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add student: {e}")
    def go_back(self):
        self.destroy()
        self.parent.deiconify() # Bring back the TeacherDashboard

# if __name__ == "__main__":
#     #  teacher_id = 1  # Replace with actual teacher ID from login
#     # app = TeacherDashboard(teacher_id)
#     # app.mainloop()
#     pass
