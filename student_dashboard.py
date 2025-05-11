import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
import oracledb
import logging

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="attendance_app.log",
)

def get_connection():
    try:
        conn = oracledb.connect(
            user="system",
            password="Server123",
            dsn="localhost/orcal"
        )
        logging.info("Database connection successful.")
        return conn
    except oracledb.DatabaseError as e:
        logging.error(f"Database Connection Failed: {e}")
        messagebox.showerror("Error", f"Database Connection Failed: {e}")
        return None

class StudentDashboard(tk.Tk):
    def __init__(self, student_id, parent=None):
        super().__init__()
        self.title("Student Dashboard")
        self.geometry("600x450")
        self.student_id = student_id
        self.parent = parent

        if self.parent:
            back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
            back_button.pack(pady=5, anchor="w", padx=10)

        label = tk.Label(self, text="Your Courses", font=("Arial", 14))
        label.pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("Course ID", "Course Name"), show="headings")
        self.tree.heading("Course ID", text="Course ID")
        self.tree.heading("Course Name", text="Course Name")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="View Attendance", font=("Arial", 12), command=self.view_attendance).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Request Leave", font=("Arial", 12), command=self.request_leave).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="View Stats", font=("Arial", 12), command=self.view_stats).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="View Overall Attendance", font=("Arial", 12), command=self.view_overall_attendance).grid(row=0, column=3, padx=5)
        tk.Button(self, text="Leave Request Status", font=("Arial", 12), command=self.view_leave_status).pack(pady=10)
        tk.Button(self, text="Logout", font=("Arial", 10), command=self.destroy).pack(pady=5)

        self.load_courses()
        self.show_leave_status = False

    def load_courses(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.course_id, c.course_name
                FROM courses c
                JOIN enrollments e ON c.course_id = e.course_id
                WHERE e.student_id = :sid
            """, {'sid': self.student_id})
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=row)
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Database Error: {e}")

    def get_selected_course(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a course.")
            return None
        return self.tree.item(selected)['values']

    def request_leave(self):
        selected_course = self.get_selected_course()
        if selected_course:
            LeaveRequestWindow(self, self.student_id, selected_course[0], selected_course[1])

    def view_attendance(self):
        selected_course = self.get_selected_course()
        if selected_course:
            AttendanceRecordsWindow(self, self.student_id, selected_course[0], selected_course[1])

    def view_stats(self):
        selected_course = self.get_selected_course()
        if selected_course:
            AttendanceStatsWindow(self, self.student_id, selected_course[0], selected_course[1])

    def view_overall_attendance(self):
        selected_course = self.get_selected_course()
        if selected_course:
            OverallAttendanceWindow(self, self.student_id, selected_course[0], selected_course[1])

    def view_leave_status(self):
        LeaveRequestStatusWindow(self, self.student_id)

    def go_back(self):
        if self.parent:
            self.destroy()
            self.parent.deiconify()
        else:
            self.destroy()

class AttendanceRecordsWindow(tk.Toplevel):
    def __init__(self, parent, student_id, course_id, course_name):
        super().__init__(parent)
        self.title(f"Attendance Records - {course_name}")
        self.geometry("600x400")
        self.parent = parent
        self.student_id = student_id
        self.course_id = course_id
        self.course_name = course_name

        tk.Label(self, text=f"Attendance Records for {course_name}", font=("Arial", 14, "bold")).pack(pady=10)
        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w", padx=10)

        tk.Label(self, text="Select Date:", font=("Arial", 10)).pack(pady=5)
        self.date_entry = DateEntry(self, width=16, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_entry.pack(pady=5)

        self.view_button = tk.Button(self, text="View Records", command=self.load_records)
        self.view_button.pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("Date", "Status"), show='headings')
        self.tree.heading("Date", text="Date")
        self.tree.heading("Status", text="Status")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.load_records()

    def load_records(self):
        selected_date = self.date_entry.get_date()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DATE_ATTENDED, STATUS
                FROM ATTENDANCE
                WHERE COURSE_ID = :cid
                AND STUDENT_ID = :sid
                AND TRUNC(DATE_ATTENDED) = TO_DATE(:selected_date, 'YYYY-MM-DD')
                ORDER BY DATE_ATTENDED ASC
            """, {'cid': self.course_id, 'sid': self.student_id, 'selected_date': selected_date})
            records = cursor.fetchall()
            self.tree.delete(*self.tree.get_children())

            for row in records:
                formatted_date = row[0].strftime('%Y-%m-%d')
                self.tree.insert('', tk.END, values=(formatted_date, row[1]))

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load attendance records: {e}")

    def go_back(self):
        self.destroy()
        self.parent.deiconify()

class LeaveRequestWindow(tk.Toplevel):
    def __init__(self, parent, student_id, course_id, course_name):
        super().__init__(parent)
        self.title("Leave Request")
        self.geometry("400x250")
        self.parent = parent

        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w", padx=10)

        tk.Label(self, text=f"Request Leave for: {course_name}", font=("Arial", 12)).pack(pady=10)
        tk.Label(self, text="Select Date:", font=("Arial", 10)).pack(pady=5)

        self.date_entry = DateEntry(self, width=16, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_entry.pack(pady=5)

        tk.Label(self, text="Reason:", font=("Arial", 10)).pack(pady=5)
        self.reason_entry = tk.Entry(self, width=40)
        self.reason_entry.pack(pady=5)

        tk.Button(self, text="Submit", command=lambda: self.submit_leave(student_id, course_id)).pack(pady=10)

    def submit_leave(self, student_id, course_id):
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
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO leave_requests (student_id, course_id, leave_date, reason, status)
                VALUES (:sid, :cid, :ldate, :reason, 'Pending')
            """, {'sid': student_id, 'cid': course_id, 'ldate': selected_date, 'reason': reason})

            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Leave request submitted successfully.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Database Error: {e}")

    def go_back(self):
        self.destroy()
        self.parent.deiconify()

class AttendanceStatsWindow(tk.Toplevel):
    def __init__(self, parent, student_id, course_id, course_name):
        super().__init__(parent)
        self.title(f"Attendance Statistics - {course_name}")
        self.geometry("400x300")
        self.parent = parent
        self.student_id = student_id
        self.course_id = course_id
        self.course_name = course_name

        tk.Label(self, text=f"Attendance Statistics for {course_name}", font=("Arial", 14, "bold")).pack(pady=10)
        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w", padx=10)

        self.stats_label = tk.Label(self, text="", font=("Arial", 12))
        self.stats_label.pack(pady=10)

        self.load_stats()

    def load_stats(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Define output variables
            present_count = cursor.var(oracledb.NUMBER)
            absent_count = cursor.var(oracledb.NUMBER)
            leave_count = cursor.var(oracledb.NUMBER)
            total_count = cursor.var(oracledb.NUMBER)

            # Call the stored procedure
            cursor.callproc('GET_ATTENDANCE_STATS',
                            [self.student_id, self.course_id, present_count, absent_count, leave_count, total_count])

            # Get the output values from the variables
            present_count_val = present_count.getvalue()
            absent_count_val = absent_count.getvalue()
            leave_count_val = leave_count.getvalue()
            total_count_val = total_count.getvalue()

            # Calculate percentages based on 16 total classes
            total_classes = 16
            present_percentage = (present_count_val / total_classes) * 100 if total_classes else 0
            absent_percentage = (absent_count_val / total_classes) * 100 if total_classes else 0
            leave_percentage = (leave_count_val / total_classes) * 100 if total_classes else 0

            # Use the returned values
            self.stats_label.config(text=(
                f"Present: {present_count_val} ({present_percentage:.2f}%)\n"
                f"Absent: {absent_count_val} ({absent_percentage:.2f}%)\n"
                f"Leave: {leave_count_val} ({leave_percentage:.2f}%)\n"
                f"Total Classes: {total_classes}"
            ))

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load attendance statistics: {e}")

    def go_back(self):
        self.destroy()
        self.parent.deiconify()

class OverallAttendanceWindow(tk.Toplevel):
    def __init__(self, parent, student_id, course_id, course_name):
        super().__init__(parent)
        self.title(f"Overall Attendance - {course_name}")
        self.geometry("600x400")
        self.parent = parent
        self.student_id = student_id
        self.course_id = course_id
        self.course_name = course_name

        tk.Label(self, text=f"Overall Attendance for {course_name}", font=("Arial", 14, "bold")).pack(pady=10)
        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w", padx=10)

        self.tree = ttk.Treeview(self, columns=("Date", "Status"), show='headings')
        self.tree.heading("Date", text="Date")
        self.tree.heading("Status", text="Status")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.load_overall_attendance()

    def load_overall_attendance(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            attendance_cursor = cursor.var(oracledb.CURSOR)
            cursor.callproc(
                "GET_OVERALL_ATTENDANCE",
                [self.student_id, self.course_id, attendance_cursor],
            )
            results = attendance_cursor.getvalue()
            if results:
                rows = results.fetchall()
                self.tree.delete(*self.tree.get_children())
                for row in rows:
                    formatted_date = row[0]
                    self.tree.insert('', tk.END, values=(formatted_date, row[1]))
                results.close()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load overall attendance: {e}")

    def go_back(self):
        self.destroy()
        self.parent.deiconify()

class LeaveRequestStatusWindow(tk.Toplevel):
    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.title("Leave Request Status")
        self.geometry("650x450")
        self.parent = parent
        self.student_id = student_id

        back_button = tk.Button(self, text="\u2190 Back", command=self.go_back, font=("Arial", 12))
        back_button.pack(pady=5, anchor="w", padx=10)

        tk.Label(self, text="Your Leave Requests", font=("Arial", 14, "bold")).pack(pady=10)

        self.leave_tree = ttk.Treeview(self, columns=("Request ID", "Course", "Date", "Reason", "Status"), show='headings')
        self.leave_tree.heading("Request ID", text="Request ID")  # Added Request ID
        for col in ("Course", "Date", "Reason", "Status"):
            self.leave_tree.heading(col, text=col)
            self.leave_tree.column(col, width=120, anchor="center")
        self.leave_tree.pack(pady=10, fill="both", expand=True)

        self.dismiss_button = tk.Button(self, text="Dismiss Selected", command=self.dismiss_leave_request, font=("Arial", 12))
        self.dismiss_button.pack(pady=10)

        self.load_leave_requests()

    def load_leave_requests(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT lr.request_id, c.course_name, TO_CHAR(lr.leave_date, 'YYYY-MM-DD'), lr.reason, lr.status
                FROM leave_requests lr
                JOIN courses c ON lr.course_id = c.course_id
                WHERE lr.student_id = :student_id
            """, {'student_id': self.student_id})

            for row in cursor.fetchall():
                self.leave_tree.insert('', tk.END, values=(row[0], row[1], row[2], row[3], row[4])) # Added row[0]

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load leave requests: {e}")

    def dismiss_leave_request(self):
        selected_item = self.leave_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a leave request to dismiss.")
            return

        request_id = self.leave_tree.item(selected_item)['values'][0]
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM leave_requests
                WHERE request_id = :request_id AND student_id = :student_id
            """, {'request_id': request_id, 'student_id': self.student_id})

            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Leave request dismissed successfully.")
            # Remove the item from the Treeview *before* reloading data
            self.leave_tree.delete(selected_item)
            self.load_leave_requests()  # Refresh the list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to dismiss leave request: {e}")

    def go_back(self):
        self.destroy()
        self.parent.deiconify()

if __name__ == "__main__":
    # Replace '21-SE-01' with the actual student ID for testing
    student_id = '21-SE-01'
    app = StudentDashboard(student_id)
    app.mainloop()
