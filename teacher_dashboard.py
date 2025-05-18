import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import datetime
import calendar
from database import get_connection
import logging
import oracledb
import uuid  # Import the uuid module

logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    filename="attendance_app.log")

# --- AddStudentWindow Definition ---
class AddStudentWindow(tk.Toplevel):
    def __init__(self, parent, course_id): # <--- Corrected to accept course_id
        super().__init__(parent)
        self.title("Add Student to Course") # <--- Corrected title
        self.geometry("300x150") # Adjusted geometry
        self.course_id = course_id # Store the course_id
        self.parent = parent

        tk.Label(self, text=f"Add Student to Course: {course_id}", font=("Arial", 12)).pack(pady=10)
        tk.Label(self, text="Student ID:").pack()
        self.student_id_entry = tk.Entry(self)
        self.student_id_entry.pack(pady=5)

        add_button = tk.Button(self, text="Add Student", command=self.add_student)
        add_button.pack(pady=10)

        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w", padx=10)


    def add_student(self):
        student_id = self.student_id_entry.get().strip()
        if not student_id:
            messagebox.showwarning("Input Error", "Please enter a student ID.")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            enrollment_id = str(uuid.uuid4())  # Generate a UUID
            query = """
    INSERT INTO enrollments_insert_view (enrollment_id, student_id, course_id)
    VALUES (:enrollment_id, :student_id, :course_id)
"""
            cursor.execute(query, {'enrollment_id': enrollment_id, 'student_id': student_id, 'course_id': self.course_id})
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", f"Student {student_id} added to course.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add student: {e}")

    def go_back(self):
        self.destroy()
        self.parent.deiconify()


class RemoveStudentWindow(tk.Toplevel):
    def __init__(self, parent, course_id):
        super().__init__(parent)
        self.title("Remove Student from Course")
        self.geometry("300x150")
        self.course_id = course_id
        self.parent = parent

        tk.Label(self, text=f"Remove Student from Course: {course_id}", font=("Arial", 12)).pack(pady=10)
        tk.Label(self, text="Student ID:").pack()
        self.student_id_entry = tk.Entry(self)
        self.student_id_entry.pack(pady=5)

        remove_button = tk.Button(self, text="Remove Student", command=self.remove_student)
        remove_button.pack(pady=10)

        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w", padx=10)

    def remove_student(self):
        student_id = self.student_id_entry.get().strip()
        if not student_id:
            messagebox.showwarning("Input Error", "Please enter a student ID.")
            return
        if not messagebox.askyesno("Confirm", f"Are you sure you want to remove student {student_id} from course {self.course_id}?"):
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
    DELETE FROM enrollments_delete_view
    WHERE student_id = :student_id AND course_id = :course_id
"""
            cursor.execute(query, {'student_id': student_id, 'course_id': self.course_id})
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", f"Student {student_id} removed from course {self.course_id}.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not remove student: {e}")

    def go_back(self):
        self.destroy()
        self.parent.deiconify()



class TeacherDashboard(tk.Tk):
    def __init__(self, teacher_id):
        super().__init__()
        self.teacher_id = teacher_id
        self.title("Teacher Dashboard")
        self.geometry("600x400") # Adjusted height

        tk.Label(self, text="Welcome to Attendance System", font=("Arial", 18, "bold")).pack(pady=10)

        self.course_listbox = tk.Listbox(self, font=("Arial", 12), width=50, height=8) # Reduced height slightly
        self.course_listbox.pack(pady=10)

        self.load_courses()

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Mark Attendance", font=("Arial", 12, "bold"), command=self.open_attendance_window).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="View Attendance Records", font=("Arial", 12), command=self.view_attendance_records).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Leave Requests", font=("Arial", 12, "bold"), command=self.view_leave_requests).grid(row=1, column=0, columnspan=2, pady=10) # Moved Leave Requests down

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

    def view_leave_requests(self):
        AllLeaveRequestsWindow(self, self.teacher_id) # Use the new window


class AllLeaveRequestsWindow(tk.Toplevel):
    def __init__(self, parent, teacher_id):
        super().__init__(parent)
        self.title("All Pending Leave Requests")
        self.geometry("700x500")
        self.teacher_id = teacher_id
        self.parent = parent

        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w", padx=10)

        tk.Label(self, text="All Pending Leave Requests", font=("Arial", 14, "bold")).pack(pady=10)

        self.leave_tree = ttk.Treeview(
            self,
            columns=("Student ID", "Course", "Leave Date", "Reason", "Status"),
            show="headings",
        )
        for col in ("Student ID", "Course", "Leave Date", "Reason", "Status"):
            self.leave_tree.heading(col, text=col)
            self.leave_tree.column(col, width=120, anchor="center")
            if col == "Reason":
                self.leave_tree.column(col, width=150)

        self.leave_tree.pack(pady=10, fill="both", expand=True)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame, text="Approve Leave", command=self.approve_leave, font=("Arial", 12)
        ).grid(row=0, column=0, padx=5)
        tk.Button(
            button_frame, text="Disapprove Leave", command=self.disapprove_leave, font=("Arial", 12)
        ).grid(row=0, column=1, padx=5)

        self.load_leave_requests()

    def load_leave_requests(self):
        """Loads all pending leave requests from the database."""
        try:
            conn = get_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute(
    """
        SELECT
            STUDENT_ID,
            COURSE_NAME,
            TO_CHAR(LEAVE_DATE, 'YYYY-MM-DD'),
            REASON,
            STATUS,
            COURSE_ID,
            TO_CHAR(LEAVE_DATE, 'YYYY-MM-DD')
        FROM pending_leave_requests_view
    """
)

            self.leave_tree.delete(*self.leave_tree.get_children())

            for row in cursor.fetchall():
                self.leave_tree.insert(
                    "", tk.END, values=(row[0], row[1], row[2], row[3], row[4])
                )

            cursor.close()
            conn.close()

        except oracledb.DatabaseError as e:
            logging.error(f"Failed to load pending leave requests: {e}")
            messagebox.showerror("Error", f"Failed to load pending leave requests: {e}")

    def approve_leave(self):
        selected_item = self.leave_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a leave request to approve.")
            return

        student_id, course_name, leave_date_str, reason, status = self.leave_tree.item(selected_item)["values"]

        if not messagebox.askyesno("Confirm", "Are you sure you want to approve this leave?"):
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Update the leave request status via the update view
            cursor.execute(
                """
                    UPDATE leave_requests_update_view
                    SET status = 'Approved'
                    WHERE STUDENT_ID = :sid
                      AND COURSE_ID = (SELECT course_id FROM course_name_id_view WHERE course_name = :cname)
                      AND LEAVE_DATE = TO_DATE(:ldate, 'YYYY-MM-DD')
                      AND REASON = :reason
                """,
                {
                    "sid": student_id,
                    "cname": course_name,
                    "ldate": leave_date_str,
                    "reason": reason,
                },
            )
            conn.commit()

            # Automatically mark attendance as 'Leave' if not already present via the merge view
            cursor.execute("""
                MERGE INTO attendance_merge_view a
                USING (SELECT :sid AS student_id,
                            (SELECT course_id FROM course_name_id_view WHERE course_name = :cname) AS course_id,
                            TO_DATE(:ldate, 'YYYY-MM-DD') AS date_attended,
                            :day_attended AS day_attended,
                            'Leave' AS status
                       FROM dual) s
                ON (a.STUDENT_ID = s.student_id AND a.COURSE_ID = s.course_id AND TRUNC(a.DATE_ATTENDED) = s.date_attended)
                WHEN NOT MATCHED THEN
                    INSERT (STUDENT_ID, COURSE_ID, DATE_ATTENDED, DAY_ATTENDED, STATUS)
                    VALUES (s.student_id, s.course_id, s.date_attended, s.day_attended, s.status)
                WHEN MATCHED THEN
                    UPDATE SET a.STATUS = s.status, a.DAY_ATTENDED = s.day_attended
            """, {
                "sid": student_id,
                "cname": course_name,
                "ldate": leave_date_str,
                "day_attended": calendar.day_name[datetime.datetime.strptime(leave_date_str, '%Y-%m-%d').weekday()]
            })
            conn.commit()

            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Leave request approved and attendance marked as 'Leave'.")
            self.load_leave_requests()  # Refresh the list
            # If the AttendanceWindow is currently open and showing the same course
            # and date, it might need a manual refresh to reflect the change.
        except oracledb.DatabaseError as e:
            messagebox.showerror("Error", f"Error approving leave: {e}")

    def disapprove_leave(self):
        selected_item = self.leave_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a leave request to disapprove.")
            return

        student_id, course_name, leave_date_str, reason, status = self.leave_tree.item(selected_item)["values"]

        if not messagebox.askyesno("Confirm", "Are you sure you want to disapprove this leave?"):
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                    UPDATE leave_requests_update_view
                    SET status = 'Rejected'
                    WHERE STUDENT_ID = :sid
                      AND COURSE_ID = (SELECT course_id FROM course_name_id_view WHERE course_name = :cname)
                      AND LEAVE_DATE = TO_DATE(:ldate, 'YYYY-MM-DD')
                      AND REASON = :reason
                """,
                {
                    "sid": student_id,
                    "cname": course_name,
                    "ldate": leave_date_str,
                    "reason": reason,
                },
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Leave request disapproved.")
            self.load_leave_requests()  # Refresh the list
        except oracledb.DatabaseError as e:
            messagebox.showerror("Error", f"Error disapproving leave: {e}")
    def go_back(self):
        self.destroy()
        self.parent.deiconify()


class AttendanceWindow(tk.Toplevel):
    def __init__(self, parent, teacher_id, course_id, course_name):
        super().__init__(parent)
        self.title(f"Mark Attendance - {course_name}")
        self.geometry("750x800")
        self.teacher_id = teacher_id
        self.course_id = course_id
        self.course_name = course_name
        self.parent = parent
        tk.Label(self, text=f"Mark Attendance for {course_name}",font=("Arial", 16, "bold")).pack(pady=10)
        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w",padx=10)
        tk.Label(self, text="Select Attendance Date:", font=("Arial", 12)).pack()
        self.date_picker = DateEntry(self, width=12, font=("Arial", 12), command=self.load_students_on_date)
        self.date_picker.pack(pady=5)

        self.students_frame = tk.Frame(self)
        self.students_frame.pack(pady=10, fill="both", expand=True)

        self.status_label = tk.Label(self.students_frame, text="Student ID - Name", font=("Arial", 12, "bold"))
        self.status_label.grid(row=0, column=0, padx=10, pady=5)
        self.attendance_label = tk.Label(self.students_frame, text="Status", font=("Arial", 12, "bold"))
        self.attendance_label.grid(row=0, column=1, padx=10, pady=5, columnspan=3)

        self.attendance_vars = {}
        self.student_widgets = {}

        self.load_students_on_date()

        save_btn = tk.Button(self, text="Save Attendance", font=("Arial", 12, "bold"), command=self.save_attendance)
        save_btn.pack(pady=10)


        update_btn = tk.Button(self, text="Update Attendance", font=("Arial", 12), command=self.update_attendance)
        update_btn.pack(pady=5)

    def load_students_on_date(self):
        for widgets in self.student_widgets.values():
            for widget in widgets:
                widget.destroy()
        self.student_widgets.clear()
        self.load_students(self.students_frame, self.date_picker.get_date())

    def load_students(self, frame, selected_date):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                SELECT s.student_id, (s.first_name || ' ' || s.last_name) AS student_name
                FROM course_students_view s
                WHERE s.course_id = :course_id
                ORDER BY s.student_id
            """
            cursor.execute(query, {'course_id': self.course_id})

            row_num = 1
            widgets_for_student = []
            for student_id, student_name in cursor.fetchall():
                student_label = tk.Label(frame, text=f"{student_id} - {student_name}", font=("Arial", 12))
                student_label.grid(row=row_num, column=0, sticky="w", padx=10, pady=5)
                widgets_for_student.append(student_label)

                initial_status = self.get_initial_attendance_status(student_id, selected_date)
                var = tk.StringVar(value=initial_status)
                self.attendance_vars[student_id] = var

                present_radio = tk.Radiobutton(frame, text="Present", variable=var, value="Present")
                present_radio.grid(row=row_num, column=1, padx=5)
                widgets_for_student.append(present_radio)
                absent_radio = tk.Radiobutton(frame, text="Absent", variable=var, value="Absent")
                absent_radio.grid(row=row_num, column=2, padx=5)
                widgets_for_student.append(absent_radio)
                leave_radio = tk.Radiobutton(frame, text="Leave", variable=var, value="Leave")
                leave_radio.grid(row=row_num, column=3, padx=5)
                widgets_for_student.append(leave_radio)

                self.student_widgets[student_id] = widgets_for_student
                widgets_for_student = []
                row_num += 1

            cursor.close()
            conn.close()
        except Exception as e:
            logging.error(f"Failed to load students: {e}")
            messagebox.showerror("Error", f"Failed to load students: {e}")


    def get_initial_attendance_status(self, student_id, selected_date):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
    SELECT status
    FROM attendance_status_view
    WHERE STUDENT_ID = :student_id
      AND COURSE_ID = :course_id
      AND TRUNC(DATE_ATTENDED) = TO_DATE(:date_attended, 'YYYY-MM-DD')
""", {
    'student_id': student_id,
    'course_id': self.course_id,
    'date_attended': selected_date.strftime('%Y-%m-%d')
})
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result:
                return result[0]
            else:
                return self.get_leave_status(student_id, selected_date)
        except Exception as e:
            logging.error(f"Failed to get initial attendance status: {e}")
            return self.get_leave_status(student_id, selected_date)

    def get_leave_status(self, student_id, selected_date):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1
                FROM leave_requests
                WHERE STUDENT_ID = :student_id
                  AND COURSE_ID = :course_id
                  AND TRUNC(LEAVE_DATE) = TO_DATE(:date_attended, 'YYYY-MM-DD')
                  AND STATUS = 'Approved'
            """, {
                'student_id': student_id,
                'course_id': self.course_id,
                'date_attended': selected_date.strftime('%Y-%m-%d')
            })
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return "Leave" if result else "Absent"
        except Exception as e:
            logging.error(f"Failed to check leave status: {e}")
            messagebox.showerror("Error", f"Failed to check leave status: {e}")
            return "Absent"

    def save_attendance(self):
        selected_date = self.date_picker.get_date()
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Check if attendance has already been taken for this course and date
            cursor.execute("""
                SELECT 1
                FROM attendance_check_view
                WHERE COURSE_ID = :cid
                  AND TRUNC(DATE_ATTENDED) = TO_DATE(:dat, 'YYYY-MM-DD')
            """, {
                'cid': self.course_id,
                'dat': selected_date.strftime('%Y-%m-%d')
            })
            attendance_already_marked = cursor.fetchone()

            if attendance_already_marked:
                messagebox.showwarning("Warning", "Attendance for this course on this date has already been marked.")
                cursor.close()
                conn.close()
                return

            for student_id, var in self.attendance_vars.items():
                status = var.get()
                # Call the stored procedure to save attendance
                cursor.callproc('save_attendance_proc', [
                    self.course_id,
                    selected_date,
                    student_id,
                    calendar.day_name[selected_date.weekday()],
                    status
                ])

            conn.commit()  # Commit all attendance records for the day
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Attendance saved.")
        except oracledb.DatabaseError as e:
            conn.rollback()
            logging.error(f"Failed to save attendance: {e}")
            messagebox.showerror("Error", f"Failed to save attendance: {e}")
        except Exception as e:
            conn.rollback()
            logging.error(f"An unexpected error occurred: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def update_attendance(self):
        selected_date = self.date_picker.get_date()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            for student_id, var in self.attendance_vars.items():
                status = var.get()
                cursor.execute("""
    UPDATE attendance_update_view
    SET STATUS = :stat
    WHERE STUDENT_ID = :sid
      AND COURSE_ID = :cid
      AND TRUNC(DATE_ATTENDED) = TO_DATE(:dat, 'YYYY-MM-DD')
""", {
    'stat': status,
    'sid': student_id,
    'cid': self.course_id,
    'dat': selected_date.strftime('%Y-%m-%d')
})
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Attendance updated.")
        except Exception as e:
            conn.rollback()
            logging.error(f"Failed to update attendance: {e}")
            messagebox.showerror("Error", f"Failed to update attendance: {e}")

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
        back_button.pack(pady=5, anchor="w", padx=10)

        tk.Label(self, text="Select Date:").pack()
        self.date_picker = DateEntry(self, width=12, font=("Arial", 12), command=lambda: self.load_records(course_id))
        self.date_picker.pack(pady=5)

        tk.Button(self, text="Load Records", command=lambda: self.load_records(course_id)).pack(pady=5)

        self.tree = ttk.Treeview(self, columns=("Student ID", "Date", "Status"), show='headings')
        for col in ("Student ID", "Date", "Status"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.course_id = course_id
        self.load_records(course_id)

    def load_records(self, course_id):
        selected_date = self.date_picker.get_date()
        formatted_date_str = selected_date.strftime('%Y-%m-%d')
        print(f"Loading records for Course ID: {course_id}, Date: {formatted_date_str}")
        try:
            conn = get_connection()
            if conn is None:
                print("Database connection failed in load_records.")
                return
            cursor = conn.cursor()
            sql_query = """
    SELECT student_id, formatted_date, STATUS
    FROM attendance_records_view
    WHERE COURSE_ID = :cid
      AND TRUNC(DATE_ATTENDED) = TO_DATE(:selected_date, 'YYYY-MM-DD')
    ORDER BY student_id ASC, DATE_ATTENDED ASC
"""
            cursor.execute(sql_query,
            {
        "cid": course_id,
        "selected_date": formatted_date_str,
    },
)
            records = cursor.fetchall()
            print(f"Number of records fetched: {len(records)}")
            self.tree.delete(*self.tree.get_children())

            for row in records:
                self.tree.insert("", tk.END, values=(row[0], row[1], row[2]))

            cursor.close()
            conn.close()

        except oracledb.DatabaseError as e:
            error_code = e.args[0].code
            error_message = e.args[0].message
            logging.error(
                f"Database Error in load_records: {e}, Code: {error_code}, Message: {error_message}"
            )
            messagebox.showerror(
                "Error", f"Failed to load attendance records: {e}"
            )
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.error(f"Unexpected error in load_records: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def go_back(self):
        self.destroy()
        self.parent.deiconify()

if __name__ == "__main__":
    teacher_id = 'T005' # Replace with actual teacher ID from login
    app = TeacherDashboard(teacher_id)
    app.mainloop()
    pass






# INSERT INTO teachers (teacher_id, first_name, last_name, date_of_birth, gender, age, contact_no, address, department_name, email, password, salary)
# VALUES ('T005', 'Muhammad', 'Ali', DATE '1988-09-22', 'Male', 36, '03456677889', 'Apt #12, Karachi', 'Mathematics', 'muhammad.ali@university.edu.pk', 'muhammad456', 100000.00);
