import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
import oracledb
import logging

# Configure logging at the module level
logging.basicConfig(
    level=logging.ERROR,  # Changed to ERROR, you can adjust as needed
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="attendance_app.log",
)


def get_connection():
    """
    Establishes a connection to the Oracle database. Handles connection errors
    and logs them. Returns a connection object or None on failure.
    """
    try:
        conn = oracledb.connect(
            user="system",
            password="Server123",
            dsn="localhost/orcal",
        )
        logging.info("Database connection successful.")
        return conn
    except oracledb.DatabaseError as e:
        error_code = e.args[0].code
        error_message = e.args[0].message
        logging.error(
            f"Database Connection Failed: {e}, Code: {error_code}, Message: {error_message}"
        )
        messagebox.showerror(
            "Error", f"Database Connection Failed: {e}"
        )  # Keep the messagebox
        return None  # Explicitly return None on failure


class StudentDashboard(tk.Tk):
    """
    Student dashboard application.  Displays courses and provides options to
    view attendance, request leave, view stats, and view overall attendance.
    """

    def __init__(self, student_id, parent=None):
        super().__init__()
        self.title("Student Dashboard")
        self.geometry("600x450")
        self.student_id = student_id
        self.parent = parent

        if self.parent:
            back_button = tk.Button(
                self, text="\u2190 Back", command=self.go_back, font=("Arial", 12)
            )
            back_button.pack(pady=5, anchor="w", padx=10)

        label = tk.Label(self, text="Your Courses", font=("Arial", 14))
        label.pack(pady=10)

        self.tree = ttk.Treeview(
            self, columns=("Course ID", "Course Name"), show="headings"
        )
        self.tree.heading("Course ID", text="Course ID")
        self.tree.heading("Course Name", text="Course Name")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="View Attendance",
            font=("Arial", 12),
            command=self.view_attendance,
        ).grid(row=0, column=0, padx=5)
        tk.Button(
            button_frame,
            text="Request Leave",
            font=("Arial", 12),
            command=self.request_leave,
        ).grid(row=0, column=1, padx=5)
        tk.Button(
            button_frame, text="View Stats", font=("Arial", 12), command=self.view_stats
        ).grid(row=0, column=2, padx=5)
        tk.Button(
            button_frame,
            text="View Overall Attendance",
            font=("Arial", 12),
            command=self.view_overall_attendance,
        ).grid(row=0, column=3, padx=5)
        tk.Button(self, text="Leave Request Status", font=("Arial", 12), command=self.view_leave_status).pack(pady=10)
        tk.Button(self, text="Logout", font=("Arial", 10), command=self.destroy).pack(
            pady=5
        )

        self.load_courses()  # Call load_courses here
        self.show_leave_status = False

    def load_courses(self):
        """Loads the courses for the student from the COURSE_ENROLLMENT_VIEW
        and populates the Treeview."""
        try:
            conn = get_connection()
            if conn is None:
                return  # Exit if connection failed
            cursor = conn.cursor()
            cursor.execute(
                """
                    SELECT course_id, course_name
                    FROM COURSE_ENROLLMENT_VIEW
                    WHERE student_id = :sid
                """,
                {"sid": self.student_id},
            )
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=row)
            cursor.close()
            conn.close()
        except oracledb.DatabaseError as e:
            error_code = e.args[0].code
            error_message = e.args[0].message
            logging.error(
                f"Database Error in load_courses: {e}, Code: {error_code}, Message: {error_message}"
            )
            messagebox.showerror("Error", f"Database Error: {e}")

    def get_selected_course(self):
        """Gets the selected course from the Treeview.

        Returns:
            tuple: (course_id, course_name) or None if no course is selected.
        """
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a course.")
            return None
        return self.tree.item(selected)["values"]

    def request_leave(self):
        """Opens the LeaveRequestWindow for the selected course."""
        selected_course = self.get_selected_course()
        if selected_course:
            LeaveRequestWindow(self, self.student_id, selected_course[0], selected_course[1])

    def view_attendance(self):
        """Opens the AttendanceRecordsWindow for the selected course."""
        selected_course = self.get_selected_course()
        if selected_course:
            AttendanceRecordsWindow(self, self.student_id, selected_course[0], selected_course[1])

    def view_stats(self):
        """Opens the AttendanceStatsWindow for the selected course."""
        selected_course = self.get_selected_course()
        if selected_course:
            AttendanceStatsWindow(self, self.student_id, selected_course[0], selected_course[1])

    def view_overall_attendance(self):
        """Opens the OverallAttendanceWindow for the selected course."""
        selected_course = self.get_selected_course()
        if selected_course:
            OverallAttendanceWindow(self, self.student_id, selected_course[0], selected_course[1])

    def view_leave_status(self):
        """Opens the LeaveRequestStatusWindow."""
        LeaveRequestStatusWindow(self, self.student_id)

    def go_back(self):
        """Goes back to the parent window."""
        if self.parent:
            self.destroy()
            self.parent.deiconify()
        else:
            self.destroy()


class AttendanceRecordsWindow(tk.Toplevel):
    """
    Displays attendance records for a specific course and student.
    """

    def __init__(self, parent, student_id, course_id, course_name):
        super().__init__(parent)
        self.title(f"Attendance Records - {course_name}")
        self.geometry("600x400")
        self.parent = parent
        self.student_id = student_id
        self.course_id = course_id
        self.course_name = course_name

        tk.Label(
            self, text=f"Attendance Records for {course_name}", font=("Arial", 14, "bold")
        ).pack(pady=10)
        back_button = tk.Button(
            self, text="\u2190 Back", command=self.go_back, font=("Arial", 12)
        )
        back_button.pack(pady=5, anchor="w", padx=10)

        tk.Label(self, text="Select Date:", font=("Arial", 10)).pack(pady=5)
        self.date_entry = DateEntry(
            self,
            width=16,
            background="darkblue",
            foreground="white",
            date_pattern="yyyy-mm-dd",
        )
        self.date_entry.pack(pady=5)

        self.view_button = tk.Button(self, text="View Records", command=self.load_records)
        self.view_button.pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("Date", "Status"), show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Status", text="Status")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.load_records()

    def load_records(self):
        """Loads attendance records for the selected date from the
        STUDENT_ATTENDANCE_VIEW."""
        selected_date = self.date_entry.get_date()
        formatted_date_str = selected_date.strftime('%Y-%m-%d')  # Format the date object
        print(f"Loading records for Student ID: {self.student_id}, Course ID: {self.course_id}, Date: {formatted_date_str}")  # Debug print
        try:
            conn = get_connection()
            if conn is None:
                print("Database connection failed in load_records.")  # Debug print
                return  # Exit if connection failed
            cursor = conn.cursor()
            sql_query = """
                SELECT date_attended, status
                FROM STUDENT_ATTENDANCE_VIEW
                WHERE course_id = :cid
                AND student_id = :sid
                AND TRUNC(date_attended) = TO_DATE(:selected_date, 'YYYY-MM-DD')
                ORDER BY date_attended ASC
            """
            print(f"Executing SQL: {sql_query} with selected_date: {formatted_date_str}")  # Debug print
            cursor.execute(
                sql_query,
                {
                    "cid": self.course_id,
                    "sid": self.student_id,
                    "selected_date": formatted_date_str,  # Use the formatted string
                },
            )
            records = cursor.fetchall()
            print(f"Number of records fetched: {len(records)}")  # Debug print
            self.tree.delete(*self.tree.get_children())

            for row in records:
                formatted_date = row[0].strftime("%Y-%m-%d")
                self.tree.insert("", tk.END, values=(formatted_date, row[1]))

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
            print(f"An unexpected error occurred: {e}")  # Catch any other errors
            logging.error(f"Unexpected error in load_records: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def go_back(self):
        """Goes back to the parent window."""
        self.destroy()
        self.parent.deiconify()


class LeaveRequestWindow(tk.Toplevel):
    """
    Window for submitting leave requests.
    """

    def __init__(self, parent, student_id, course_id, course_name):
        super().__init__(parent)
        self.title("Leave Request")
        self.geometry("400x250")
        self.parent = parent

        back_button = tk.Button(
            self, text="\u2190 Back", command=self.go_back, font=("Arial", 12)
        )
        back_button.pack(pady=5, anchor="w", padx=10)

        tk.Label(self, text=f"Request Leave for: {course_name}", font=("Arial", 12)).pack(
            pady=10
        )
        tk.Label(self, text="Select Date:", font=("Arial", 10)).pack(pady=5)

        self.date_entry = DateEntry(
            self,
            width=16,
            background="darkblue",
            foreground="white",
            date_pattern="yyyy-mm-dd",
        )
        self.date_entry.pack(pady=5)

        tk.Label(self, text="Reason:", font=("Arial", 10)).pack(pady=5)
        self.reason_entry = tk.Entry(self, width=40)
        self.reason_entry.pack(pady=5)

        tk.Button(
            self, command=lambda: self.submit_leave(student_id, course_id), text="Submit"
        ).pack(pady=10)

    def submit_leave(self, student_id, course_id):
        """Submits the leave request."""
        selected_date = self.date_entry.get_date()
        today = date.today()

        if selected_date < today:
            messagebox.showerror("Error", "Cannot apply for leave for a past date.")
            return

        reason = self.reason_entry.get()
        if not reason:
            messagebox.showerror("Error", "Please enter a reason for leave.")
            return

        try:
            conn = get_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute(
                """
                    INSERT INTO leave_requests (student_id, course_id, leave_date, reason, status)
                    VALUES (:sid, :cid, :ldate, :reason, 'Pending')
                """,
                {
                    "sid": student_id,
                    "cid": course_id,
                    "ldate": selected_date,
                    "reason": reason,
                },
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Leave request submitted successfully.")
            self.destroy()
        except oracledb.DatabaseError as e:
            error_code = e.args[0].code
            error_message = e.args[0].message
            logging.error(
                f"Database Error in submit_leave: {e}, Code: {error_code}, Message: {error_message}"
            )
            if error_code == 20001:  # Check for the custom error code
                messagebox.showerror("Error", error_message)
            else:
                messagebox.showerror("Error", f"Database Error: {e}")




    def go_back(self):
        """Goes back to the parent window."""
        self.destroy()
        self.parent.deiconify()


class AttendanceStatsWindow(tk.Toplevel):
    """
    Displays attendance statistics for a specific course and student using
    the ATTENDANCE_STATS_VIEW.
    """

    def __init__(self, parent, student_id, course_id, course_name):
        super().__init__(parent)
        self.title(f"Attendance Statistics - {course_name}")
        self.geometry("400x300")
        self.parent = parent
        self.student_id = student_id
        self.course_id = course_id
        self.course_name = course_name

        tk.Label(
            self, text=f"Attendance Statistics for {course_name}", font=("Arial", 14, "bold")
        ).pack(pady=10)
        back_button = tk.Button(
            self, text="\u2190 Back", command=self.go_back, font=("Arial", 12)
        )
        back_button.pack(pady=5, anchor="w", padx=10)

        self.stats_label = tk.Label(self, text="", font=("Arial", 12))
        self.stats_label.pack(pady=10)

        self.load_stats()

    def load_stats(self):
        """Loads and displays attendance statistics from the ATTENDANCE_STATS_VIEW."""
        try:
            conn = get_connection()
            if conn is None:
                return  # Exit if connection failed
            cursor = conn.cursor()
            cursor.execute(
                """
                    SELECT present_count, absent_count, leave_count, total_classes
                    FROM ATTENDANCE_STATS_VIEW
                    WHERE student_id = :sid AND course_id = :cid
                """,
                {"sid": self.student_id, "cid": self.course_id},
            )
            result = cursor.fetchone()

            if result:
                present_count_val, absent_count_val, leave_count_val, total_classes =result

                # Handle potential None values by converting them to 0
                present_count_val = present_count_val if present_count_val is not None else 0
                absent_count_val = absent_count_val if absent_count_val is not None else 0
                leave_count_val = leave_count_val if leave_count_val is not None else 0
                total_classes = total_classes if total_classes is not None else 16 # Default if not available

                present_percentage = (present_count_val / total_classes) * 100 if total_classes else 0
                absent_percentage = (absent_count_val / total_classes) * 100 if total_classes else 0
                leave_percentage = (leave_count_val / total_classes) * 100 if total_classes else 0

                self.stats_label.config(
                    text=(
                        f"Present: {present_count_val} ({present_percentage:.2f}%)\n"
                        f"Absent: {absent_count_val} ({absent_percentage:.2f}%)\n"
                        f"Leave: {leave_count_val} ({leave_percentage:.2f}%)\n"
                        f"Total Classes: {total_classes}"
                    )
                )
            else:
                self.stats_label.config(text="No statistics available for this course.")

            cursor.close()
            conn.close()

        except oracledb.DatabaseError as e:
            error_code = e.args[0].code
            error_message = e.args[0].message
            logging.error(
                f"Database Error in load_stats: {e}, Code: {error_code}, Message: {error_message}"
            )
            messagebox.showerror(
                "Error", f"Failed to load attendance statistics: {e}"
            )

    def go_back(self):
        """Goes back to the parent window."""
        self.destroy()
        self.parent.deiconify()


class OverallAttendanceWindow(tk.Toplevel):
    """
    Displays overall attendance for a specific course and student using
    the OVERALL_ATTENDANCE_VIEW.
    """

    def __init__(self, parent, student_id, course_id, course_name):
        super().__init__(parent)
        self.title(f"Overall Attendance - {course_name}")
        self.geometry("600x400")
        self.parent = parent
        self.student_id = student_id
        self.course_id = course_id
        self.course_name = course_name

        tk.Label(
            self, text=f"Overall Attendance for {course_name}", font=("Arial", 14, "bold")
        ).pack(pady=10)
        back_button = tk.Button(
            self, text="\u2190 Back", command=self.go_back, font=("Arial", 12)
        )
        back_button.pack(pady=5, anchor="w", padx=10)

        self.tree = ttk.Treeview(self, columns=("Date", "Status"), show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Status", text="Status")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.load_overall_attendance()

    def load_overall_attendance(self):
        """Loads and displays overall attendance from the OVERALL_ATTENDANCE_VIEW."""
        try:
            conn = get_connection()
            if conn is None:
                return  # Exit if connection failed
            cursor = conn.cursor()
            cursor.execute(
                """
                    SELECT date_attended, status
                    FROM OVERALL_ATTENDANCE_VIEW
                    WHERE student_id = :sid AND course_id = :cid
                    ORDER BY date_attended ASC
                """,
                {"sid": self.student_id, "cid": self.course_id},
            )
            records = cursor.fetchall()
            self.tree.delete(*self.tree.get_children())
            for row in records:
                formatted_date = row[0].strftime("%Y-%m-%d")
                self.tree.insert("", tk.END, values=(formatted_date, row[1]))
            cursor.close()
            conn.close()
        except oracledb.DatabaseError as e:
            error_code = e.args[0].code
            error_message = e.args[0].message
            logging.error(
                f"Database Error in load_overall_attendance: {e}, Code: {error_code}, Message: {error_message}"
            )
            messagebox.showerror(
                "Error", f"Failed to load overall attendance: {e}"
            )

    def go_back(self):
        """Goes back to the parent window."""
        self.destroy()
        self.parent.deiconify()


class LeaveRequestStatusWindow(tk.Toplevel):
    """
    Displays the status of leave requests for a student using the
    PENDING_LEAVE_REQUESTS_VIEW.
    """

    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.title("Leave Request Status")
        self.geometry("650x450")
        self.parent = parent
        self.student_id = student_id

        back_button = tk.Button(
            self, text="\u2190 Back", command=self.go_back, font=("Arial", 12)
        )
        back_button.pack(pady=5, anchor="w", padx=10)

        tk.Label(self, text="Your Leave Requests", font=("Arial", 14, "bold")).pack(
            pady=10
        )

        self.leave_tree = ttk.Treeview(
            self,
            columns=("Course", "Date", "Reason", "Status"),
            show="headings",
        )
        for col in ("Course", "Date", "Reason", "Status"):
            self.leave_tree.heading(col, text=col)
            self.leave_tree.column(col, width=120, anchor="center")
        self.leave_tree.pack(pady=10, fill="both", expand=True)

        self.dismiss_button = tk.Button(
            self, text="Dismiss Selected", command=self.dismiss_leave_request, font=("Arial", 12)
        )
        self.dismiss_button.pack(pady=10)

        self.load_leave_requests()

    def load_leave_requests(self):
        """Loads pending leave requests for the student from the
        PENDING_LEAVE_REQUESTS_VIEW."""
        try:
            conn = get_connection()
            if conn is None:
                return  # Exit if connection failed
            cursor = conn.cursor()
            cursor.execute(
                """
                    SELECT course_name, TO_CHAR(leave_date, 'YYYY-MM-DD'), reason, status
                    FROM PENDING_LEAVE_REQUESTS_VIEW
                    WHERE student_id = :student_id
                """,
                {"student_id": self.student_id},
            )

            self.leave_tree.delete(*self.leave_tree.get_children())  # Clear previous data

            for row in cursor.fetchall():
                self.leave_tree.insert(
                    "", tk.END, values=(row[0], row[1], row[2], row[3])
                )

            cursor.close()
            conn.close()

        except oracledb.DatabaseError as e:
            error_code = e.args[0].code
            error_message = e.args[0].message
            logging.error(
                f"Failed to load leave requests from view: {e}, Code: {error_code}, Message: {error_message}"
            )
            messagebox.showerror("Error", f"Failed to load leave requests: {e}")

    def dismiss_leave_request(self):
        """Dismisses the selected leave request by updating its status in the
        underlying LEAVE_REQUESTS table."""
        selected_item = self.leave_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a leave request to dismiss.")
            return

        course_name, leave_date_str, reason, status = self.leave_tree.item(selected_item)["values"]
        try:
            conn = get_connection()
            if conn is None:
                return  # Exit if connection failed
            cursor = conn.cursor()
            cursor.execute(
                """
                    UPDATE leave_requests
                    SET status = 'Dismissed'
                    WHERE student_id = :student_id
                      AND COURSE_ID = (SELECT course_id FROM courses WHERE course_name = :course_name)
                      AND LEAVE_DATE = TO_DATE(:leave_date, 'YYYY-MM-DD')
                      AND reason = :reason
                """,
                {
                    "student_id": self.student_id,
                    "course_name": course_name,
                    "leave_date": leave_date_str,
                    "reason": reason,
                },
            )

            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Leave request dismissed successfully.")
            self.load_leave_requests()  # Refresh the list from the view
        except oracledb.DatabaseError as e:
            error_code = e.args[0].code
            error_message = e.args[0].message
            logging.error(
                f"Failed to dismiss leave request: {e}, Code: {error_code}, Message: {error_message}"
            )
            messagebox.showerror("Error", f"Failed to dismiss leave request: {e}")

    def go_back(self):
        """Goes back to the parent window."""
        self.destroy()
        self.parent.deiconify()


if __name__ == "__main__":
    # Replace '22-SE-21' with the actual student ID for testing
    student_id = "22-SE-21"
    app = StudentDashboard(student_id)
    app.mainloop()




    
# INSERT INTO students (student_id, first_name, last_name, date_of_birth, gender, age, contact_no, address, department_name, email, password)
# VALUES ('22-SE-21', 'Junaid', 'Khan', DATE '2002-08-03', 'Male', 23, '03221122334', 'House #4A, Gujranwala', 'Software Engineering', 'junaid.khan@university.edu.pk', 'junaid6789');
