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
                INSERT INTO enrollments (enrollment_id, student_id, course_id)
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
                DELETE FROM enrollments
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
                        lr.STUDENT_ID,
                        c.COURSE_NAME,
                        TO_CHAR(lr.LEAVE_DATE, 'YYYY-MM-DD'),
                        lr.REASON,
                        lr.STATUS
                    FROM leave_requests lr
                    JOIN courses c ON lr.COURSE_ID = c.COURSE_ID
                    WHERE lr.STATUS = 'Pending'
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
            cursor.execute(
                """
                    UPDATE leave_requests
                    SET status = 'Approved'
                    WHERE STUDENT_ID = :sid
                      AND COURSE_ID = (SELECT course_id FROM courses WHERE course_name = :cname)
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
            messagebox.showinfo("Success", "Leave request approved.")
            self.load_leave_requests()  # Refresh the list
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
                    UPDATE leave_requests
                    SET status = 'Rejected'
                    WHERE STUDENT_ID = :sid
                      AND COURSE_ID = (SELECT course_id FROM courses WHERE course_name = :cname)
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
        self.geometry("750x600")
        self.teacher_id = teacher_id
        self.course_id = course_id
        self.course_name = course_name
        self.parent = parent
        tk.Label(self, text=f"Mark Attendance for {course_name}", font=("Arial", 16, "bold")).pack(pady=10)
        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w", padx=10)
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
        """
        Loads the list of students enrolled in the current course from the database
        and displays them in the provided frame with attendance status options
        (Present, Absent, Leave). It also pre-selects 'Leave' if a student has an
        approved leave for the selected date.

        Args:
            frame (tk.Frame): The Tkinter frame where the student list and
                             attendance options will be displayed.
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                SELECT s.student_id, (s.first_name || ' ' || s.last_name) AS student_name
                FROM course_students_view s
                WHERE s.course_id = :course_id
            """
            cursor.execute(query, {'course_id': self.course_id})

            # Iterate through each student fetched from the database
            for idx, (student_id, student_name) in enumerate(cursor.fetchall(), start=1):
                # Display the student ID and name in the frame
                tk.Label(frame, text=f"{student_id} - {student_name}", font=("Arial", 12)).grid(row=idx, column=0, sticky="w", padx=10, pady=5)

                # Determine the initial attendance status for the student.
                # It checks if the student has an approved leave for the currently
                # selected date in the da(
                # te picker.
                initial_status = self.get_leave_status(student_id, self.date_picker.get_date())

                # Create a Tkinter StringVar to hold the attendance status for this student.
                # Initialize it with the determined initial status.
                var = tk.StringVar(value=initial_status)

                # If the initial status is 'Leave', display a non-interactive label
                # indicating that the leave is approved. Otherwise, create radio buttons
                # for 'Present', 'Absent', and 'Leave' options.
                if var.get() == "Leave":
                    tk.Label(frame, text="Leave (Approved)", font=("Arial", 12, "bold")).grid(row=idx, column=1, padx=5, columnspan=3)
                else:
                    tk.Radiobutton(frame, text="Present", variable=var, value="Present").grid(row=idx, column=1, padx=5)
                    tk.Radiobutton(frame, text="Absent", variable=var, value="Absent").grid(row=idx, column=2, padx=5)
                    tk.Radiobutton(frame, text="Leave", variable=var, value="Leave").grid(row=idx, column=3, padx=5)

                # Store the StringVar for this student's attendance status in the
                # self.attendance_vars dictionary, using the student ID as the key.
                self.attendance_vars[student_id] = var

            cursor.close()
            conn.close()
        except Exception as e:
            logging.error(f"Failed to load students: {e}")
            messagebox.showerror("Error", f"Failed to load students: {e}")

    def get_leave_status(self, student_id, selected_date):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT plrv.status
                FROM PENDING_LEAVE_REQUESTS_VIEW plrv
                WHERE plrv.student_id = :student_id
                AND TO_DATE(plrv.leave_date, 'YYYY-MM-DD') = TO_DATE(:date_attended, 'YYYY-MM-DD')
                AND plrv.status = 'Approved' -- Still checking for 'Approved' status
            """, {
                'student_id': student_id,
                'date_attended': selected_date.strftime('%Y-%m-%d')
            })

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            return result[0] if result else "Present"

        except Exception as e:
            logging.error(f"Failed to check leave status: {e}")
            messagebox.showerror("Error", f"Failed to check leave status: {e}")
            return "Present"


    def save_attendance(self):
        """
        Saves the marked attendance for the selected date into the database.
        It iterates through the students and their selected attendance status,
        checks if an approved leave exists for the student on that date,
        and then inserts or updates the attendance record accordingly.
        """
        selected_date = self.date_picker.get_date()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Iterate through each student and their selected attendance status
            for student_id, var in self.attendance_vars.items():
                status = var.get()

                # Check if the student has an approved leave for the selected date
                cursor.execute("""
                    SELECT plrv.status
                    FROM PENDING_LEAVE_REQUESTS_VIEW plrv
                    WHERE plrv.student_id = :student_id
                    AND TO_DATE(plrv.leave_date, 'YYYY-MM-DD') = TO_DATE(:date_attended, 'YYYY-MM-DD')
                    AND plrv.status = 'Approved'
                """, {
                    'student_id': student_id,
                    'date_attended': selected_date.strftime('%Y-%m-%d')
                })

                leave_result = cursor.fetchone()
                # If an approved leave exists, force the status to 'Leave'
                if leave_result:
                    status = 'Leave'

                # Insert the attendance record into the ATTENDANCE table
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

            # Commit the changes to the database
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Attendance saved.")
            self.destroy()
            self.master.deiconify()

        except Exception as e:
            logging.error(f"Failed to save attendance: {e}")
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

        self.course_id = course_id
        self.load_records(course_id)

    def load_records(self, course_id):
        """Loads attendance records for the selected date from the database."""
        selected_date = self.date_picker.get_date()
        formatted_date_str = selected_date.strftime('%Y-%m-%d') # Format the date object
        print(f"Loading records for Course ID: {course_id}, Date: {formatted_date_str}") # Debug print
        try:
            conn = get_connection()
            if conn is None:
                print("Database connection failed in load_records.") # Debug print
                return # Exit if connection failed
            cursor = conn.cursor()
            sql_query = """
                SELECT s.student_id, TO_CHAR(a.DATE_ATTENDED, 'YYYY-MM-DD'), a.STATUS
                FROM ATTENDANCE a
                JOIN enrollments e ON a.STUDENT_ID = e.STUDENT_ID AND a.COURSE_ID = e.COURSE_ID
                JOIN students s ON e.STUDENT_ID = s.student_id
                WHERE a.COURSE_ID = :cid
                AND TRUNC(a.DATE_ATTENDED) = TO_DATE(:selected_date, 'YYYY-MM-DD')
                ORDER BY s.student_id ASC, a.DATE_ATTENDED ASC
            """
            print(f"Executing SQL: {sql_query} with course_id: {course_id}, selected_date: {formatted_date_str}") # Debug print
            cursor.execute(
                sql_query,
                {
                    "cid": course_id,
                    "selected_date": formatted_date_str, # Use the formatted string
                },
            )
            records = cursor.fetchall()
            print(f"Number of records fetched: {len(records)}") # Debug print
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
            print(f"An unexpected error occurred: {e}") # Catch any other errors
            logging.error(f"Unexpected error in load_records: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def go_back(self):
        self.destroy()
        self.parent.deiconify()

if __name__ == "__main__":
    teacher_id = 'T004' # Replace with actual teacher ID from login
    app = TeacherDashboard(teacher_id)
    app.mainloop()
    pass